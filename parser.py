#!/usr/bin/env python3
import argparse
import os
from jinja2 import Environment, FileSystemLoader
from wirebackupparser.wireAPI import WireApi
from wirebackupparser.groups import Groups
from wirebackupparser.events import Events
from wirebackupparser.stats import Stats
from wirebackupparser.backupFile import WireBackup


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',  help='backup file downloaded from Wire client', required=True)
    parser.add_argument('-g', '--group', help='name of group to use', required=True)
    parser.add_argument('-o', '--output', help='directory in which output files should be saved', default=os.curdir)
    args = parser.parse_args()

    assetsDir = os.path.join(args.output, 'assets')
    if not os.path.exists(assetsDir):
        os.mkdir(assetsDir)

    backup = WireBackup(args.file)
    session = WireApi()
    
    # parse backup file
    groups = Groups(backup)
    events = Events(backup, session)

    # generate statistics
    stats = Stats(events, groups.getGroupByName(args.group))
    # stats.dumpVariousStats()

    events.downloadAllAssetsInGroup(group=groups.getGroupByName(args.group),
                                             assetsDir=assetsDir)

    # render html version of backup
    with open('templates/main.html', 'r', encoding='utf-8') as f:
        template = Environment(loader=FileSystemLoader("templates")).from_string(f.read())
    
    out = template.render(events=events.getEventsFromGroup(groups.getGroupByName("III MI")), stats=stats, group=groups.getGroupByName("III MI"))
    
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(out)
