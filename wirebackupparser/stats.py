import dateutil.parser
from datetime import timezone


class Stats:
    def __init__(self, events, group):
        self.events = events.getEventsFromGroup(group)
        self.group = group
        self.users = group.getMembers()
        
    def calculateStats(self):
        self.reactsGiven = self.calculate_reactsGiven()
        self.reactsReceived = self.calculate_reactsReceived()
        self.reactsDistribution = self.calculate_reactsDistribution()
        self.selfAdoration = self.calculate_selfAdoration()
        self.usersShare = self.calculate_usersShare()
        self.hourDistribution = self.calculate_hourDistribution()
        self.monthDistribution = self.calculate_monthDistribution()
        self.bestMessages = self.calculate_bestMessages()

    def calculate_reactsGiven(self):
        counts = {}

        for user in self.users:
            counts[str(user)] = 0

        for event in self.events:
            for user in event.reactions:
                counts[str(user)] += 1
                
        return Stats.countify(counts, share=True)

    def calculate_reactsReceived(self):
        counts = {}

        for user in self.users:
            counts[str(user)] = 0

        for event in self.events:
            counts[str(event.origin)] += len(event.reactions)
            
        return Stats.countify(counts, share=True)
            
    def calculate_reactsDistribution(self):
        distribution = {}
        maxLikes = 0

        for event in self.events:
            likes = len(event.reactions)
            distribution[likes] = distribution.get(likes, 0) + 1
            maxLikes = max(maxLikes, likes)

        for i in range(0, maxLikes):
            if i not in distribution:
                distribution[i] = 0
                
        return Stats.countify(distribution, share=True, sortField=0, reverse=False)

    def calculate_usersShare(self):
        counts = {}

        for user in self.users:
            counts[str(user)] = 0

        for event in self.events:
            counts[str(event.origin)] += 1
            
        return Stats.countify(counts, share=True)

    def calculate_bestMessages(self):
        output = {}
        years = []
        
        for event in self.events:
            time = dateutil.parser.isoparse(event.time)
            
            if time.year == 1970:
                continue
            
            if time.year not in years:
                years += [time.year]
                
        for year in years:
            top = filter(lambda x: x.time.startswith(str(year)), self.events)
            top = sorted(top, key=lambda x: len(x.reactions), reverse=True)[:10]
            output[year] = top
        
        return output.items()

    def calculate_selfAdoration(self):
        counts = {}

        for user in self.users:
            counts[str(user)] = 0

        for event in self.events:
            if event.origin in event.reactions:
                counts[str(event.origin)] += 1
                
        return Stats.countify(counts)

    def calculate_hourDistribution(self):
        distribution = {}
        for i in range(0, 24):
            distribution[i] = 0

        for event in self.events:
            hour = dateutil.parser.isoparse(event.time)
            hour = hour.replace(tzinfo=timezone.utc).astimezone(tz=None)
            hour = hour.hour

            distribution[hour] += 1
            
        return Stats.countify(distribution, histo=True, sortField=0, reverse=False)

    def calculate_monthDistribution(self):
        distribution = {}
        for event in self.events:
            time = dateutil.parser.isoparse(event.time)
            if time.year == 1970:
                continue
            time = time.strftime("%Y-%m")

            distribution[time] = distribution.get(time, 0) + 1
            
        return Stats.countify(distribution, stringSort=True, histo=True, sortField=0, reverse=False)
    
    @staticmethod
    def countify(data, sortField=1, stringSort=False, reverse=True, share=False, histo=False):
        output = []
        total = 0
        maxValue = 0
        
        for key in data:
            total += data[key]
            maxValue = max(maxValue, data[key])
            
        for key in data:
            entry = [[key, data[key]]]
            
            if share:
                if total != 0:
                    entry[0] += [str(round(data[key] / total * 100, 2)) + "%"]
                else:
                    entry[0] += ["0%"]
            if histo:
                if total != 0:
                    percentage = data[key] / total
                    normalized = percentage / (maxValue / total)
                    entry[0] += [normalized * 100]
                else:
                    entry[0] += [0]
                
            entry[0] += [total]
            output += entry
        
        if not stringSort:
            output = sorted(output, key=lambda x: int(x[sortField]), reverse=reverse)
        else:
            output = sorted(output, key=lambda x: str(x[sortField]), reverse=reverse)
        
        return output
