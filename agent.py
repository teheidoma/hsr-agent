import json
import os
import sys
import threading
import time

from flask import Flask, request
from flask_cors import CORS

import system
from fileparser import FileParser
import requests
import subprocess
import webbrowser
import pyautogui

from status import Status, ErrorCode, AgentStatus
from storage import Storage
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)
parser = FileParser()
storage = Storage()

debug = True
APP_VERSION = '0.1.1'
status: Status = Status()

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

    link_device()
    return '{"status":"OK"}'


def get_agent_update_url():
    resp = requests.get(API_BASE_URL + '/agent/info',
                        auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                        verify=False)
    return resp.json()


@app.route("/status", methods=['GET'])
def get_status():
    print(status.to_response())
    return status.to_response()


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
            resp = requests.get(API_BASE_URL + '/agent/commands',
                                auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                                verify=False)
            for command in resp.json():
                print(command)
                print(command['type'])
                result = ''
                if command['type'] == 'CMD':
                    result = exec_cmd(command)
                if command['type'] == 'SCREENSHOT':
                    result = screenshot(command)
                agent_send_response(command, result)
        time.sleep(2)


def link_device():
    auth_token = get_honkai_token()
    if auth_token:
        requests.post(API_BASE_URL + '/registration/link', json={"token": auth_token},
                      auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                      verify=False)
        status.status(AgentStatus.IMPORT)


def init_reg():
    if not storage.has_value('token'):
        webbrowser.open(APP_BASE_URL + '/registration/token')


def get_honkai_token():
    status.clear()
    req = requests.get(API_BASE_URL + '/agent/pull',
                       auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                       verify=False).text
    print(req)
    with open('temp.ps1', 'w') as temp_file:
        temp_file.write(req)
        temp_file.flush()
    run = subprocess.run('powershell ./temp.ps1', capture_output='stdout')
    os.remove('temp.ps1')
    print(run.stdout)
    resp = json.loads(run.stdout)
    print(resp)
    if resp['status'] == 'SUCCESS':
        auth_key = \
        next(filter(lambda f: f[0] == 'authkey', map(lambda x: x.split("="), list(str(resp['token']).split("&")))))[1]
        return auth_key
    else:
        status.error(resp['code'])
        return None


t = threading.Thread(target=pull_agent_commands, daemon=True)
t.start()
init_reg()
app.run(port=25565, host='0.0.0.0')
