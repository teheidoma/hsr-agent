import requests


class Logger(object):
    def __init__(self, url, storage):
        self.url = url
        self.storage = storage

    def log(self, message, printLog=True, level='INFO', sendLog=True):
        if sendLog:
            try:
                requests.post(self.url + '/logs', json={'message': message, 'level': level},
                              auth=requests.auth.HTTPBasicAuth(self.storage.get_value('id'),
                                                               self.storage.get_value('token')), ).status_code
            except Exception as e:
                print(e)
        if printLog:
            print(f'[{level}]: {message}')
