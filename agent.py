import json
import logging
import os
import sys
import threading
import time

from flask import Flask, request
from flask_cors import CORS, cross_origin

import system
from fileparser import FileParser
import requests
import subprocess
import webbrowser
import pyautogui

from storage import Storage
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)
parser = FileParser()
storage = Storage()

debug = True
APP_VERSION = '0.1.1'

if debug:
    API_BASE_URL = 'http://localhost:8080'
    APP_BASE_URL = 'http://localhost:4200'
else:
    API_BASE_URL = 'https://hsrapi.teheidoma.com'
    APP_BASE_URL = 'https://hsr.teheidoma.com'


@app.route("/token", methods=['POST'])
def install():
    print(request.json)
    storage.set_value('token', request.json['token'])
    storage.set_value('id', request.json['id'])
    storage.save()

    return get_honkai_token()


def get_agent_update_url():
    resp = requests.get(API_BASE_URL + '/agent/info',
                        auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                        verify=False)
    return resp.json()


def exec_cmd(command):
    os.system('chcp 65001')
    run = subprocess.check_output('cmd /c ' + command['command'], encoding='utf-8', text=True)
    print(sys.stdout.encoding)
    with open('f.txt', 'w', encoding='utf-8') as f:
        f.write(run)
        f.close()
    return run


def agent_send_response(command, result):
    requests.post(API_BASE_URL + '/agent/result',
                  headers={
                      'Content-Type': 'application/json;charset=utf-8'
                  },
                  json={'id': command['id'], 'result': result},
                  auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                  verify=False)


def screenshot(command):
    filename = f'{command["id"]}.png'
    pyautogui.screenshot(filename)
    with open(filename, 'rb') as f:
        print(requests.put(command['command'], data=f.read()))
    return 'https://hsr.teheidoma.com:9000/screenshot/' + filename


def pull_agent_commands():
    while True:
        if storage.has_value('id'):
            try:
                resp = requests.get(API_BASE_URL + '/agent/commands',
                                    auth=requests.auth.HTTPBasicAuth(storage.get_value('id'),
                                                                     storage.get_value('token')),
                                    verify=False)
            except Exception as e:
                print(e)
                break
            for command in resp.json():
                try:
                    print(command)
                    print(command['type'])
                    result = ''
                    if command['type'] == 'CMD':
                        result = exec_cmd(command)
                    if command['type'] == 'SCREENSHOT':
                        result = screenshot(command)
                    agent_send_response(command, result)
                except Exception as e:
                    agent_send_response(command, e.__str__())

        time.sleep(2)


def get_honkai_token():
    req = requests.get(API_BASE_URL + '/agent/pull',
                       auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                       verify=False).text
    with open('temp.ps1', 'w') as temp_file:
        temp_file.write(req)
        temp_file.flush()
    run = subprocess.run('powershell ./temp.ps1', capture_output='stdout')
    os.remove('temp.ps1')

    resp = json.loads(run.stdout)
    return resp


t = threading.Thread(target=pull_agent_commands, daemon=True)
t.start()
app.run(port=25565, host='0.0.0.0')
print(123)
