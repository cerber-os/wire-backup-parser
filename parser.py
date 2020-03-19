#!/usr/bin/env python3
import os
import json
from jinja2 import Template
from terminaltables import SingleTable
from tqdm import tqdm
from time import sleep
from wireAPI import WireApi
from groups import Groups
from events import Events
from stats import Stats



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
    
    # converastion info
    groups = Groups(convs)
    groups.dumpGroups()

    # login via WireApi
    session = WireApi()

    # collect and filter events
    events = Events(events, session)

    # generate some fancy statistics
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
    with open('./summarytemplate.html', 'r') as f:
        tm = Template(f.read())
    out = tm.render(events=events, stats=stats, groups=groups)
    with open('./output.html', 'w') as f:
        f.write(out)
