from wirebackupparser.events import ProxyUser

ENT_TYPE_GROUP = 0
ENT_TYPE_DIRECT = 2


class Group:
    def __init__(self, uid, name, creator, others, backupOwner):
        self.id = uid
        self.name = name
        self.creator = ProxyUser(creator) if creator else None
        self.members = [ProxyUser(o) for o in others] if others else []
        if self.creator and self.creator not in self.members:
            self.members.append(self.creator)
        self.members.append(ProxyUser(backupOwner))

    def __str__(self):
        return self.name

    def getId(self):
        return self.id

    def getMembers(self):
        result = []
        for user in self.members:
            try:
                result.append(user.name)
            except ValueError:
                # Return only valid users
                pass
        return self.members


class Groups:
    """
    Despite what name might suggest, this class handles both direct messages and group conversations.
    Don't blame me, this is how Wire developers decided to implement backup format
    """
    groups = []
    directGroups = []

    def __init__(self, backup):
        for conv in backup.convs:
            if conv.get('type') == ENT_TYPE_GROUP:
                self.groups.append(Group(conv.get('id'),
                                         conv.get('name'),
                                         conv.get('creator'),
                                         conv.get('others'),
                                         backupOwner=backup.backupOwner))
            elif conv.get('type') == ENT_TYPE_DIRECT:
                self.directGroups.append(Group(conv.get('id'),
                                               name="Direct conversation",
                                               creator=None,
                                               others=conv.get('others'),
                                               backupOwner=backup.backupOwner))
            else:
                # Ignore other types of conversations
                pass

    def getGroupByName(self, name):
        for group in self.groups:
            if group.name == name:
                return group
        raise KeyError("Unknown group with name {}".format(name))

    def getGroups(self):
        return self.groups

    def getDirectGroupByUserID(self, userID):
        for directGroup in self.directGroups:
            if directGroup.members[0] == userID:
                return directGroup
        raise KeyError("Unknown direct group with member {}".format(userID))

    def getDirectGroups(self):
        return self.directGroups
