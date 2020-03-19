EVT_TYPE_MSG_ADD = 'conversation.message-add'
EVT_TYPE_ASSET_ADD = 'conversation.asset-add'
EVT_TYPE_KNOCK = 'conversation.knock'

Users = []


# TODO: Move it to class
def getUserByID(id):
    for user in Users:
        if user.id == id:
            return user
    raise KeyError("Cannot find user {} in provided dict".format(id))


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
        self.origin = ProxyUser(event['from'])
        self.time = event['time']
        self.type = event['type']
        self.reactions = [ProxyUser(user) for user in event.get('reactions', [])]

        if self.type == EVT_TYPE_MSG_ADD:
            self.message = event['data']['content']
        elif self.type == EVT_TYPE_ASSET_ADD:
            self.img_type = event['data']['content_type']
            self.img_sha256 = event['data'].get('sha256')
            self.img_otr_key = event['data'].get('otr_key')
            self.img_key = event['data'].get('key', '')
            self.img_token = event['data'].get('token')
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


class Events:
    events = []

    def __init__(self, events, session=None):
        global Users
        for event in events:
            e = Event(event)
            self.events.append(e)
            if e.origin not in Users:
                Users.append(User(e.origin.id))
        self.events = sorted(self.events, key=lambda x: x.time)

        if session:
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
        return [e for e in self.getEventsFromGroup(group) if e.type == EVT_TYPE_ASSET_ADD and e.img_key]
