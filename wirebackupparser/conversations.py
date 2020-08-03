from wirebackupparser.events import ProxyUser, getUserByID

ENT_TYPE_GROUP = 0
ENT_TYPE_DIRECT = 2


class Conversation:
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


class Conversations:
    groups = []
    directGroups = []

    def __init__(self, backup):
        for conv in backup.convs:
            if conv.get('type') == ENT_TYPE_GROUP:
                self.groups.append(Conversation(conv.get('id'),
                                                conv.get('name'),
                                                conv.get('creator'),
                                                conv.get('others'),
                                                backupOwner=backup.backupOwner))
            elif conv.get('type') == ENT_TYPE_DIRECT and len(conv.get('others')) > 0:
                try:
                    self.directGroups.append(Conversation(conv.get('id'),
                                                          name=getUserByID(conv.get('others')[0]).name,
                                                          creator=conv.get('creator'),
                                                          others=conv.get('others'),
                                                          backupOwner=backup.backupOwner))
                except KeyError:
                    # Handle cases, when direct communication is established with user that no longer exists
                    pass
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
            if userID in directGroup.members:
                return directGroup
        raise KeyError("Unknown direct group with member {}".format(userID))

    def getDirectGroups(self):
        return self.directGroups
