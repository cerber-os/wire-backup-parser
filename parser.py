#!/usr/bin/env python3
import argparse
import os
from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm
from time import sleep
from wirebackupparser.wireAPI import WireApi
from wirebackupparser.groups import Groups
from wirebackupparser.events import Events
from wirebackupparser.stats import Stats
from wirebackupparser.backupFile import WireBackup


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',  help='backup file downloaded from Wire client', required=True)
    parser.add_argument('-g', '--group', help='TODO: some nice help here', required=True)
    parser.add_argument('-o', '--output', help='directory in which output files should be saved', default=os.curdir)
    args = parser.parse_args()

    backup = WireBackup(args.file)
    session = WireApi()
    
    # parse backup file
    groups = Groups(backup)
    events = Events(backup, session)

    # generate statistics
    stats = Stats(events, groups.getGroupByName(args.group))
    # stats.dumpVariousStats()

    assets = events.getAllAssetsInGroup(groups.getGroupByName(args.group))
    print("Dumping {} assets".format(len(assets)))
    for event in tqdm(assets):
        fileName = './assets/{}'.format(event.asset_key.replace('/', ''))
        if os.path.exists(fileName):
            continue
        
        if not session.isOtrKeyValid(event.asset_otr_key):
            continue

        key = session.convertOtrKey(event.asset_otr_key)
        print(fileName)
        asset = session.downloadAsset(event.asset_key, key, event.asset_token)

        with open(fileName, 'wb') as f:
            f.write(asset)
        sleep(0.50)

    # render html version of backup
    with open('templates/main.html', 'r', encoding='utf-8') as f:
        template = Environment(loader=FileSystemLoader("templates")).from_string(f.read())
    
    out = template.render(events=events.getEventsFromGroup(groups.getGroupByName("III MI")), stats=stats, group=groups.getGroupByName("III MI"))
    
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(out)
