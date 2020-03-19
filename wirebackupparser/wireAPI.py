import getpass
import os
import requests
import json
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify


class WireApi:
    def __init__(self, outputDir):
        self.email = None
        self.password = None
        self.access_token = None
        self.outputDir = outputDir

    def _loginPrompt(self):
        print("Wire credentials are required to continue")
        self.email = input("Email: ")
        self.password = getpass.getpass()

    def _login(self):
        if not self.access_token:
            self._loginPrompt()
        resp = requests.post('https://prod-nginz-https.wire.com/login',
                             json={'email': self.email, 'password': self.password},
                             headers={
                                 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
                                 'Content-Type': 'application/json'})
        if resp.status_code != 200:
            raise ConnectionError("Request failed with status {}".format(resp.status_code))
        try:
            respJson = json.loads(resp.text)
            self.access_token = respJson['access_token']
        except (json.JSONDecodeError, KeyError):
            raise ValueError("Invalid email or passsword - server returned {}".format(resp.text))

    @staticmethod
    def isOtrKeyValid(otr_key):
        # A bit dummy, but sufficient for now
        return '0' in otr_key

    @staticmethod
    def convertOtrKey(otr_key):
        return hexlify(bytes([otr_key[str(k)] for k in range(32)]))

    @staticmethod
    def _decryptImage(encryptedImg, key):
        key = unhexlify(key)
        iv = encryptedImg[:16]
        data = encryptedImg[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        pt_bytes = cipher.decrypt(data)
        return pt_bytes

    def downloadAsset(self, assetID, assetKey, assetToken, retryOn403=True):
        if not self.access_token:
            self._login()
        params = {'access_token': self.access_token, 'asset_token': assetToken}  # , 'forceCaching': "true"}
        resp = requests.get('https://prod-nginz-https.wire.com/assets/v3/{}'.format(assetID),
                            params=params,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'})
        if resp.status_code == 404:
            return None
        elif resp.status_code == 403 and retryOn403:
            # Access token can expire before download of all assets finishes
            self._login()
            self.downloadAsset(assetID, assetKey, assetToken, False)
        elif resp.status_code != 200:
            raise ConnectionError("Request failed with status {}".format(resp.status_code))

        return self._decryptImage(resp.content, assetKey)

    def getUsersList(self, usersIDs, retryOn403=True):
        if os.path.exists('./users.json'):
            with open('./users.json', 'r') as f:
                return json.load(f)
        if not self.access_token:
            self._login()
        params = {'ids': ','.join(usersIDs)}
        resp = requests.get('https://prod-nginz-https.wire.com/users',
                            params=params,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
                                'Authorization': 'Bearer ' + self.access_token})
        if resp.status_code == 403 and retryOn403:
            self._login()
            self.getUsersList(usersIDs, False)
        elif resp.status_code != 200:
            raise ConnectionError("Request failed with status {} - {}".format(resp.status_code, resp.text))
        try:
            respJson = json.loads(resp.text)
        except json.JSONDecodeError:
            raise ConnectionError("Invalid response from server: {}".format(resp.text))

        with open('./users.json', 'w') as f:
            json.dump(respJson, f)
        return respJson
