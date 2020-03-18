from terminaltables import SingleTable

ENT_TYPE_GROUP = 0


class Group:
    def __init__(self, uid, name, others):
        self.id = uid
        self.name = name
        self.others = others

    def __str__(self):
        return self.name

    def getId(self):
        return self.id


class Groups:
    groups = []

    def __init__(self, convs):
        for conv in convs:
            # Only parse groups
            if conv.get('type') != ENT_TYPE_GROUP:
                continue

            self.groups.append(Group(conv.get('id'), conv.get('name'), conv.get('others')))
            # TODO: conv['creator'] and conv['others']

    def dumpGroups(self):
        data = [["ID[:6]", "Name", "Member count"]]

        for group in self.groups:
            data.append([group.id[:6], group.name, len(group.others) + 1])

        table_instance = SingleTable(data, "Group conversations")
        print(table_instance.table)

    def getGroupByName(self, name):
        for group in self.groups:
            if group.name == name:
                return group
        raise KeyError("Unknown group with name {}".format(name))

    def getGroups(self):
        return self.groups
