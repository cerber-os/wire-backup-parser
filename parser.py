#!/usr/bin/env python3
import getpass
import json
from terminaltables import SingleTable
from textwrap import wrap

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

#############################################
# Conversation parsing
#############################################
ENT_TYPE_GROUP = 0

Conversations = []

def collectConversations(convs):
    for conv in convs:
        # only include group convos
        if conv['type'] != ENT_TYPE_GROUP:
            continue
        
        row = {
            'name': conv['name'],
            'id': conv['id'],
        }
        if 'creator' in conv:
            row['creator'] = conv['creator']
        if 'others' in conv:
            row['others'] = conv['others']
        
        Conversations.append(row)
     
def listConversations():    
    data = [["ID[:6]", "Name", "Member count"]]
    
    for group in Conversations:
        data.append([group['id'][:6], group['name'], len(group['others']) + 1])
        
    table_instance = SingleTable(data, "Group conversations")
    print(table_instance.table)

#############################################
# Events parsing
#############################################
EVT_TYPE_MSG_ADD = 'conversation.message-add'
EVT_TYPE_ASSET_ADD = 'conversation.asset-add'
EVT_TYPE_KNOCK = 'conversation.knock'

MI3 = '94dde542-02b8-4ebf-92d1-cf5ff5798a07'
PREDEFINED_USERS = {
    '474bf8fd-bb2e-4cba-aada-ddefb4c7e146': 'Przemu',
    'faea135f-20b6-4677-aecd-b24dc623e45d': 'Dominik',
    '5ccb807c-d4c7-4ce5-860c-473713dcc316': '3na10',
    '335a86d8-bed9-497c-b98d-aff1ec4adaf9': 'Lachcim',
    '4f4edecb-84a2-4d34-9ae2-1909ee4ef03a': 'Szymon',
    '4ab302da-aefe-4df9-b314-690e9357b10c': 'Żewi',
    'f832bd3a-68fd-4acc-8ff9-0a14fc8a3470': 'Karol', 
    '9cab97e0-43c1-4271-b6cc-b48da002e875': 'Jagoda',
    '3e4869c6-c46a-4d1f-831b-4f4867ac9dbe': 'Cycuel',
    'a4254b98-6adb-49f1-b2f9-27e2c8051e86': 'Damian',
    'c19103b5-bd0b-4e08-b632-209fb3a68b0c': 'DarkRob',
    '11638a43-0074-4152-8379-11d803d9d628': 'Budziło'
}

Events = []

class Event:
    conv_id = ''
    id = ''
    origin = ''
    time = ''
    type = ''
    reactions = {}
    
    message = ''
    
    img_type = ''
    img_width = ''
    img_height = ''
    img_key = ''
    img_token = ''
    img_sha256 = ''
    img_otr_key = ''
    
    def __init__(self, event):
        self.conv_id = event['conversation']
        self.origin = event['from']
        self.time = event['time']
        self.type = event['type']
        
        self.origin = PREDEFINED_USERS.get(self.origin, '\033[33m' + self.origin + '\033[0m')
        
        self.reactions = event.get('reactions')
        
        if self.type == EVT_TYPE_MSG_ADD:
            self.message = event['data']['content']
        elif self.type == EVT_TYPE_ASSET_ADD:
            self.img_type = event['data']['content_type']
            self.img_sha256 = event['data'].get('sha256')
            self.img_otr_key = event['data'].get('otr_key')
        else:
            pass

    def __str__(self):
        if self.type == EVT_TYPE_MSG_ADD:
            return "[{}] MSG <{}>: {}".format(self.time, self.origin, self.message)
        elif self.type == EVT_TYPE_ASSET_ADD:
            return "[{}] IMAGE <{}> ID<{}>".format(self.time, self.origin, self.img_token)
        elif self.type == EVT_TYPE_KNOCK:
            return "[{}] PING <{}>".format(self.time, self.origin)
        else:
            return "[{}] UNKNOWN <{}>".format(self.time, self.origin)

def collectEvents(events):
    global Events
    
    for event in events:
        Events.append(Event(event))
    
    Events = sorted(Events, key=lambda x: x.time)
        
def listEvents():
    for event in Events:
        if event.conv_id != MI3:
            continue
        
        print(event)

#############################################
# Statistics parser
#############################################
def printStat_reactsGiven():
    users = {}
    for user in PREDEFINED_USERS:
        users[user] = 0
    
    for event in Events:
        if event.conv_id == MI3 and event.reactions is not None:
            for key in event.reactions:
                users[key] += 1
    
    stats = []
    for user in users:
        stats.append([PREDEFINED_USERS[user], str(users[user])])
    stats = sorted(stats, key=lambda x: int(x[1]), reverse=True)
    stats = [["Username", "Count"]] + stats
    
    table_instance = SingleTable(stats, "Reacts given")
    table_instance.justify_columns[1] = 'right'
    print(table_instance.table)

def printStat_messagesLikedBy(user):
    msgs = filter(lambda x: x.conv_id == MI3, Events)
    msgs = filter(lambda x: user in (x.reactions or []), msgs)
    
    printMessages("Messages liked by {}".format(PREDEFINED_USERS[user]), msgs)

def printStat_usersShare():
    counts = {}
    total = 0
    
    for user in PREDEFINED_USERS:
        counts[PREDEFINED_USERS[user]] = 0
    
    for event in Events:
        if event.conv_id == MI3:
            total += 1
            counts[event.origin] += 1
    
    entries = []
    for key in counts:
        entries += [[key, str(counts[key]), str(round(counts[key] / total * 100, 2)) + '%']]
    entries = sorted(entries, key=lambda x: int(x[1]), reverse=True)
    
    entries = [["Author", "Amount", "Share"]] + entries
    entries += [["Total", str(total), "100%"]]
    
    table_instance = SingleTable(entries, "Users share in messages")
    table_instance.justify_columns[2] = 'right'
    table_instance.inner_footing_row_border = True
    print(table_instance.table)
    
def printStat_bestMessages(year):
    top = filter(lambda x: x.conv_id == MI3, Events)
    top = filter(lambda x: x.time.startswith(str(year)), top)
    top = sorted(top, key=lambda x: len(x.reactions or []), reverse=True)
    
    printMessages("Best messages of {}".format(year), top, includeLikes=True)
    
def printMessages(title, messages, includeLikes=False, maxCount=10):
    data = [["Author", "Message", "Date"]]
    if includeLikes:
        data[0] += ["Likes"]
        
    table_instance = SingleTable(data, title)
    count = 0
    
    for message in messages:
        entry = [message.origin]
        
        if message.type == EVT_TYPE_ASSET_ADD:
            entry += ["Asset {}".format(message.img_type)]
        else:
            entry += ['\n'.join(wrap(message.message, 50))[:200]]
        
        entry += [message.time]
        if includeLikes:
            entry += [str(len(message.reactions))]
        
        count += 1
        data += [entry]
        
        if count == maxCount:
            break
            
    if (includeLikes):
        table_instance.justify_columns[3] = 'right'
    print(table_instance.table)
    
#############################################
# Image download
#############################################
def getAccessToken(email, password):
    import requests
    resp = requests.post('https://prod-nginz-https.wire.com/login', 
        json={'email': email, 'password': password},
        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0', 'Content-Type': 'application/json'})
    return json.loads(resp.text).get('access_token')
    
#############################################
# Main
#############################################
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
    collectConversations(convs)
    listConversations()
    
    # statistics
    collectEvents(events)
    printStat_reactsGiven()
    printStat_messagesLikedBy('11638a43-0074-4152-8379-11d803d9d628') # budzidlo
    printStat_usersShare()
    for year in range(2017, 2021):
        printStat_bestMessages(year)
        
    print("Preparing for dumping images")
    print("Wire credentials are required")
    email = input("Email: ")
    password = getpass.getpass()
    
    print("Requesting access token")
    accessToken = getAccessToken(email, password)
    email = password = None
    print("Your access token: ", accessToken)
     
