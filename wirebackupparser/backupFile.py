import json
from zipfile import ZipFile


class WireBackup:
    def __init__(self, backupArchiveName):
        with ZipFile(backupArchiveName) as backup:
            with backup.open('events.json') as eventsJSON:
                self.events = json.load(eventsJSON)

            with backup.open('conversations.json') as convsJSON:
                self.convs = json.load(convsJSON)

            with backup.open('export.json') as backupJSON:
                self.backupInfo = json.load(backupJSON)

            self.backupOwner = self.backupInfo['user_id']

    def getBackupInfo(self):
        return self.backupInfo
