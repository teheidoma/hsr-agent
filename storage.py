import json
import os


class Storage:
    data = {}

    def __init__(self):
        self.load()

    def save(self):
        with open('config.json', 'w') as file:
            json.dump(self.data, file)

    def load(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as file:
                self.data = json.load(file)

    def set_value(self, key, value):
        self.data[key] = value

    def has_value(self, key) -> bool:
        return key in self.data

    def get_value(self, key):
        return self.data[key]
