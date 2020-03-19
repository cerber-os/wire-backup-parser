import dateutil.parser
from datetime import timezone
from textwrap import wrap
from terminaltables import SingleTable
from events import EVT_TYPE_ASSET_ADD, getUserByID


class Stats:
    def __init__(self, events, group):
        self.events = events
        self.group = group

    def printStat_reactsGiven(self):
        counts = {}

        for user in self.events.getUsers():
            counts[str(user)] = 0

        for event in self.events.getEventsFromGroup(self.group):
            for user in event.reactions:
                counts[str(user)] += 1

        self.printCounts("Reacts given", counts, showShare=True)

    def printStat_reactsReceived(self):
        counts = {}

        for user in self.events.getUsers():
            counts[str(user)] = 0

        for event in self.events.getEventsFromGroup(self.group):
            counts[str(event.origin)] += len(event.reactions)

        self.printCounts("Reacts received", counts, showShare=True)

    def printStat_reactsDistribution(self):
        distribution = {}
        maxLikes = 0

        for event in self.events.getEventsFromGroup(self.group):
            likes = len(event.reactions)
            distribution[likes] = distribution.get(likes, 0) + 1
            maxLikes = max(maxLikes, likes)

        for i in range(0, maxLikes):
            if i not in distribution:
                distribution[i] = 0

        self.printCounts("Distribution of likes", distribution, sort="key_asc", showShare=True, dataKey="Likes",
                         dataValue="Messages")

    def printStat_messagesLikedBy(self, user):
        msgs = filter(lambda x: user in x.reactions, self.events.getEventsFromGroup(self.group))
        self.printMessages("Messages liked by {}".format(str(user)), msgs)

    def printStat_usersShare(self):
        counts = {}

        for user in self.events.getUsers():
            counts[str(user)] = 0

        for event in self.events.getEventsFromGroup(self.group):
            counts[str(event.origin)] += 1

        self.printCounts("Users share in messages", counts, showShare=True)

    def printStat_bestMessages(self, year):
        top = filter(lambda x: x.time.startswith(str(year)), self.events.getEventsFromGroup(self.group))
        top = sorted(top, key=lambda x: len(x.reactions), reverse=True)
        self.printMessages("Best messages of {}".format(year), top, includeLikes=True)

    def printStat_selfAdoration(self):
        counts = {}

        for user in self.events.getUsers():
            counts[str(user)] = 0

        for event in self.events.getEventsFromGroup(self.group):
            if event.origin in event.reactions:
                counts[str(event.origin)] += 1
        self.printCounts("Self-awarded likes", counts)

    def printStat_hourDistribution(self):
        distribution = {}
        for i in range(0, 24):
            distribution[i] = 0

        for event in self.events.getEventsFromGroup(self.group):
            hour = dateutil.parser.isoparse(event.time)
            hour = hour.replace(tzinfo=timezone.utc).astimezone(tz=None)
            hour = hour.hour

            distribution[hour] += 1

        self.printCounts("Distirbution by time", distribution, sort="key_asc", showShare=True, histoShare=True,
                         dataKey="Hour",
                         dataValue="Messages")

    def printStat_monthDistribution(self):
        distribution = {}
        for event in self.events.getEventsFromGroup(self.group):
            time = dateutil.parser.isoparse(event.time)
            if time.year == 1970:
                continue
            time = time.strftime("%Y-%m")

            distribution[time] = distribution.get(time, 0) + 1

        self.printCounts("Distirbution by period", distribution, sort="key_alpha_asc", showShare=True, histoShare=True,
                         dataKey="Period", dataValue="Messages")

    @staticmethod
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

        if includeLikes:
            table_instance.justify_columns[3] = 'right'
        print(table_instance.table)

    @staticmethod
    def printCounts(title, data, showShare=False, histoShare=False, sort="value_desc", dataKey="Author",
                    dataValue="Amount"):
        entries = []
        total = 0
        maxValue = 0

        for key in data:
            total += data[key]
            maxValue = max(maxValue, data[key])

        for key in data:
            entry = [[key, data[key]]]
            if showShare:
                if histoShare:
                    percentage = data[key] / total
                    normalized = percentage / (maxValue / total)

                    entry[0] += [u"\u2588" * round(normalized * 25)]
                else:
                    entry[0] += [str(round(data[key] / total * 100, 2)) + "%"]

            entries += entry

        if sort:
            if "_alpha_" in sort:
                sortfun = lambda x: str(x[sort.startswith("value_")])
            else:
                sortfun = lambda x: int(x[sort.startswith("value_")])

            entries = sorted(entries, key=sortfun, reverse=sort.endswith("_desc"))

        header = [dataKey, dataValue]
        footer = ["Total", total]
        if showShare:
            header += ["Share"]
            footer += ["100%"]
        entries = [header] + entries + [footer]

        table_instance = SingleTable(entries, title)
        table_instance.justify_columns[1] = "right"
        table_instance.justify_columns[2] = "right" if not histoShare else "left"
        table_instance.inner_footing_row_border = True
        print(table_instance.table)

    def dumpVariousStats(self):
        self.printStat_reactsGiven()
        self.printStat_reactsReceived()
        self.printStat_reactsDistribution()
        try:
            self.printStat_messagesLikedBy(getUserByID('11638a43-0074-4152-8379-11d803d9d628'))  # budzidlo
        except KeyError:
            print("No such user {}".format('11638a43-0074-4152-8379-11d803d9d628'))
        self.printStat_usersShare()
        self.printStat_selfAdoration()
        self.printStat_hourDistribution()
        self.printStat_monthDistribution()
        for year in range(2017, 2021):
            self.printStat_bestMessages(year)
