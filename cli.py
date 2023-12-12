import os

import requests
import time

ID = 'a8ec0284-b017-40a9-88f7-d6466893ea35'
TOKEN = 'ffdc7833-6ff6-4003-bfa3-88bd803f65cc'

DEVICE = 'a8ec0284-b017-40a9-88f7-d6466893ea35'
URL = 'http://localhost:8080'

headers = {
    'Content-Type': 'application/json',
}

while True:
    command = input("Enter command: ")
    data = {}
    if command == 'SCREENSHOT':
        data = {
            'type': 'SCREENSHOT',
            'deviceId': DEVICE
        }
    else:
        data = {
            'command': command,
            'type': 'CMD',
            'deviceId': DEVICE
        }

    response = requests.post(URL + '/agent/command', headers=headers, json=data, auth=(ID, TOKEN))

    command_id = response.text
    print(command_id)
    while True:
        time.sleep(1)
        get_response = requests.get(URL + '/agent/result?commandId=' + command_id, auth=(ID, TOKEN))
        if len(get_response.content) > 0:
            print(get_response.text.replace('\\n', '\n'))
            break
