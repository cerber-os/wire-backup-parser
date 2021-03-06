#!/usr/bin/env python3
import argparse
import os

from htmlmin.minify import html_minify
from jinja2 import Environment, FileSystemLoader

from wirebackupparser.backupFile import WireBackup
from wirebackupparser.events import Events, getUserByName
from wirebackupparser.conversations import Conversations
from wirebackupparser.stats import Stats
from wirebackupparser.utils import genThumbsForFilesInDir
from wirebackupparser.wireAPI import WireApi


def createWorkingDir(arg):
    outputDir = os.path.join(arg, 'output')
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    assetsDir = os.path.join(outputDir, 'assets')
    if not os.path.exists(assetsDir):
        os.mkdir(assetsDir)
    thumbsDir = os.path.join(assetsDir, 'thumbnails')
    if not os.path.exists(thumbsDir):
        os.mkdir(thumbsDir)
    return outputDir, assetsDir, thumbsDir


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command-line tool for creating reports and statistics of Wire '
                                                 'conversations')
    parser.add_argument('-f', '--file', help='backup file downloaded from Wire client', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--group', help='the name of group to use')
    group.add_argument('-u', '--user', help='the name of user to use')
    group.add_argument('--uid', help='ID of user to use')
    parser.add_argument('-o', '--output', help='directory in which output files should be saved', default=os.curdir)
    args = parser.parse_args()

    outputDir, assetsDir, thumbsDir = createWorkingDir(args.output)

    print("Loading backup...")
    backup = WireBackup(args.file)
    session = WireApi(outputDir=outputDir)

    # parse backup file
    print("Parsing backup...")
    events = Events(backup, session)
    groups = Conversations(backup)

    if args.group:
        target = groups.getGroupByName(args.group)
    elif args.user:
        try:
            target = groups.getDirectGroupByUserID(getUserByName(args.user))
        except KeyError as e:
            print("[+] Ambigous username! Try again with option --uid")
            exit(1)
    elif args.uid:
        target = groups.getDirectGroupByUserID(args.uid)

    # generate statistics
    print("Generating stats...")
    stats = Stats(events, target)
    stats.calculateStats()

    # Download assets
    events.downloadAllAssetsInGroup(group=target,
                                    assetsDir=assetsDir)
    genThumbsForFilesInDir(assetsDir, thumbsDir)

    # Render html report
    print("Generating HTML report...")
    with open('templates/main.html', 'r', encoding='utf-8') as f:
        env = Environment(trim_blocks=True, lstrip_blocks=True, loader=FileSystemLoader("templates")).from_string(
            f.read())

    out = env.render(events=events.getEventsFromGroup(target),
                     stats=stats,
                     group=target,
                     export=backup.getBackupInfo())

    with open(os.path.join(outputDir, 'report.html'), 'w', encoding='utf-8') as f:
        f.write(html_minify(out))

    print("Generated report: file://{}".format(os.path.abspath(os.path.join(outputDir, "report.html"))))
