#!/usr/bin/env python3
import os
import json
from jinja2 import Environment, FileSystemLoader
from terminaltables import SingleTable
from tqdm import tqdm
from time import sleep
from wirebackupparser.wireAPI import WireApi
from wirebackupparser.groups import Groups, BackupOwner
from wirebackupparser.events import Events
from wirebackupparser.stats import Stats


def printExportInfo(exportInfo):
    pkg_info = (
        ("Created on", exportInfo.get('creation_time', '[None]')),
        ("Username", exportInfo.get('user_name', '[None]')),
        ("Version", str(exportInfo.get('version', '[None]'))),
    )
    
    table_instance = SingleTable(pkg_info, "Export Info")
    table_instance.justify_columns[1] = 'right'
    table_instance.inner_heading_row_border = False
    
    print(table_instance.table)


if __name__ == '__main__':
    with open('./export.json', 'r', encoding='utf-8') as f:
        exportInfo = json.load(f)
        
    with open('./events.json', 'r', encoding='utf-8') as f:
        events = json.load(f)
    
    with open('./conversations.json', 'r', encoding='utf-8') as f:
        convs = json.load(f)
    
    # export info
    printExportInfo(exportInfo)
    import wirebackupparser.groups
    wirebackupparser.groups.BackupOwner = exportInfo['user_id']
    
    # conversation info
    groups = Groups(convs)
    groups.dumpGroups()

    # login via WireApi
    session = WireApi()

    # collect and filter events
    events = Events(events, session)

    # generate statistics
    stats = Stats(events, groups.getGroupByName("III MI"))
    stats.dumpVariousStats()

    images = events.getAllAssetsInGroup(groups.getGroupByName("III MI"))
    print("Starting dump of {} images".format(len(images)))
    for event in tqdm(images):
        fileName = './images/{}.img'.format(event.img_key.replace('/', ''))
        if os.path.exists(fileName):
            continue
        
        if not session.isOtrKeyValid(event.img_otr_key):
            continue

        key = session.convertOtrKey(event.img_otr_key)
        asset = session.downloadAsset(event.img_key, key, event.img_token)

        with open(fileName, 'wb') as f:
            f.write(asset)
        sleep(0.50)

    # render html version of backup
    with open('templates/main.html', 'r', encoding='utf-8') as f:
        template = Environment(loader=FileSystemLoader("templates")).from_string(f.read())
    
    out = template.render(events=events.getAllEvents(), stats=stats, groups=groups)
    
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(out)
