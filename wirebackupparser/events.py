import os
from tqdm import tqdm
from time import sleep

EVT_TYPE_MSG_ADD = 'conversation.message-add'
EVT_TYPE_ASSET_ADD = 'conversation.asset-add'
EVT_TYPE_KNOCK = 'conversation.knock'
EVT_TYPE_CONV_RENAME = 'conversation.rename'
EVT_TYPE_CONV_JOIN = 'conversation.member-join'
EVT_TYPE_CONV_LEAVE = 'conversation.member-leave'
EVT_TYPE_CONV_LOCATION = 'conversation.location'
EVT_TYPE_UNABLE_TO_DECRYPT = 'conversation.unable-to-decrypt'
EVT_TYPE_DELETE_MSG = 'conversation.delete-everywhere'

Users = []


# TODO: Move it to class
def getUserByID(uid):
    for user in Users:
        if user.id == uid:
            return user
    raise KeyError("Cannot find user {} in provided dict".format(uid))


def getUserByName(name):
    result = [user for user in Users if user.name == name]
    if len(result) > 1:
        raise KeyError("Ambigious username {} - found {} times".format(name, len(result)))
    return result[0]


class User:
    def __init__(self, uid):
        self.id = uid
        self.name = None

    def fillFromDict(self, d):
        for user in d:
            if self.id == user['id']:
                self.name = user.get('name', user.get('handler', self.id))
                # TODO: user['picture'] and user['assets']
                return
        raise KeyError("Cannot find user {} in provided dict".format(self.id))

    def __str__(self):
        return self.name if self.name else self.id

    def __eq__(self, other):
        if type(other) is str:
            return self.id == other or self.name == other
        elif type(other) is User or type(other) is ProxyUser:
            return self.id == other.id
        else:
            raise TypeError("__eq__ is only implemented to str type (not {})".format(type(other)))


class ProxyUser:
    def __init__(self, uid):
        self.id = uid

    def __getattr__(self, item):
        if item == 'id':
            return self.id
        for user in Users:
            if user.id == self.id:
                getattr(user, item)
        raise ValueError("No user with id {}".format(self.id))

    def __str__(self):
        for user in Users:
            if user.id == self.id:
                return user.__str__()
        return "ProxyUser<{}>".format(self.id)

    def __eq__(self, other):
        if type(other) is ProxyUser:
            return self.id == other.id
        for user in Users:
            if user.id == self.id:
                return user.__eq__(other)
        return self.id == other


class Event:
    def __init__(self, event):
        self.conv_id = event['conversation']
        self.id = event.get('id')
        self.origin = ProxyUser(event['from'])
        self.time = event['time']
        self.type = event['type']
        self.reactions = [ProxyUser(user) for user in event.get('reactions', [])]

        if self.type == EVT_TYPE_MSG_ADD:
            self.message = event['data']['content']
            if type(event['data'].get('quote')) is dict:
                self.quote_from = ProxyUser(event['data']['quote'].get('user_id'))
                self.quote_msg_id = event['data']['quote'].get('message_id')
            else:
                self.quote_msg = self.quote_msg = None
        elif self.type == EVT_TYPE_ASSET_ADD:
            self.asset_name = event['data'].get('info', {}).get('name')
            self.asset_type = event['data']['content_type']
            self.asset_sha256 = event['data'].get('sha256')
            self.asset_otr_key = event['data'].get('otr_key')
            self.asset_key = event['data'].get('key', '')
            self.asset_token = event['data'].get('token')
            
            if self.asset_type.startswith("image/"):
                self.asset_kind = "image"
            elif self.asset_type.startswith("audio/"):
                self.asset_kind = "audio"
            elif self.asset_type.startswith("video/"):
                self.asset_kind = "video"
            else:
                self.asset_kind = "other"
        elif self.type == EVT_TYPE_CONV_RENAME:
            self.new_name = event['data']['name']
        elif self.type in [EVT_TYPE_CONV_JOIN, EVT_TYPE_CONV_LEAVE]:
            self.target_users = [ProxyUser(u) for u in event['data']['user_ids']]
        elif self.type == EVT_TYPE_CONV_LOCATION:
            self.longitude = event['data']['location']['longitude']
            self.latitude = event['data']['location']['latitude']
            self.location_name = event['data']['location']['name']
            self.location_zoom = event['data']['location']['zoom']
        elif self.type == EVT_TYPE_UNABLE_TO_DECRYPT:
            self.reason = event['error']
        elif self.type == EVT_TYPE_DELETE_MSG:
            self.when = event['data']['deleted_time']
        else:
            pass

    def __str__(self):
        if self.type == EVT_TYPE_MSG_ADD:
            return "[{}] MSG <{}>: {}".format(self.time, self.origin, self.message)
        elif self.type == EVT_TYPE_ASSET_ADD:
            return "[{}] ASSET <{}> ID<{}>".format(self.time, self.origin, self.asset_token)
        elif self.type == EVT_TYPE_KNOCK:
            return "[{}] PING <{}>".format(self.time, self.origin)
        else:
            return "[{}] UNKNOWN <{}>".format(self.time, self.origin)


class Events:
    events = []

    def __init__(self, backup, session=None):
        global Users
        events = backup.events
        for event in events:
            e = Event(event)
            self.events.append(e)
            if e.origin not in Users:
                Users.append(User(e.origin.id))
        self.events = sorted(self.events, key=lambda x: x.time)

        self.session = session
        ids = [user.id for user in Users]
        d = session.getUsersList(ids)
        for user in Users:
            user.fillFromDict(d)

    def getAllEvents(self):
        return self.events

    def getEventsFromGroup(self, group):
        return [x for x in self.events if x.conv_id == group.id]

    @staticmethod
    def getUsers():
        return Users

    def getAllAssetsInGroup(self, group):
        return [e for e in self.getEventsFromGroup(group) if e.type == EVT_TYPE_ASSET_ADD and e.asset_key]

    def downloadAllAssetsInGroup(self, group, assetsDir):
        print("Downloading assets...")
        assets = self.getAllAssetsInGroup(group)
        for event in tqdm(assets):
            fileName = os.path.join(assetsDir, event.asset_key.replace('/', ''))
            if os.path.exists(fileName) or not self.session.isOtrKeyValid(event.asset_otr_key):
                continue

            key = self.session.convertOtrKey(event.asset_otr_key)
            asset = self.session.downloadAsset(event.asset_key, key, event.asset_token)
            with open(fileName, 'wb') as f:
                f.write(asset)

            # Prevent overloading remote server
            sleep(0.50)
