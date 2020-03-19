from terminaltables import SingleTable
from wirebackupparser.events import ProxyUser

ENT_TYPE_GROUP = 0


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
    groups = []

    def __init__(self, backup):
        for conv in backup.convs:
            # Only parse groups
            if conv.get('type') != ENT_TYPE_GROUP:
                continue

            self.groups.append(Group(conv.get('id'),
                                     conv.get('name'),
                                     conv.get('creator'),
                                     conv.get('others'),
                                     backupOwner=backup.backupOwner))

    def dumpGroups(self):
        data = [["ID[:6]", "Name", "Member count"]]

        for group in self.groups:
            data.append([group.id[:6], group.name, len(group.members)])

        table_instance = SingleTable(data, "Group conversations")
        print(table_instance.table)

    def getGroupByName(self, name):
        for group in self.groups:
            if group.name == name:
                return group
        raise KeyError("Unknown group with name {}".format(name))

    def getGroups(self):
        return self.groups
