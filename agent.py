import os
import threading

from flask import Flask, request
from flask_cors import CORS

import agent_status
import system
from fileparser import FileParser
import requests
import subprocess
import webbrowser

from storage import Storage
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)
parser = FileParser()
storage = Storage()

API_BASE_URL = 'https://hsrapi.teheidoma.com'
APP_BASE_URL = 'http://localhost:4200'
# APP_BASE_URL = 'https://hsr.teheidoma.com'

honkai_token = None


@app.route("/token", methods=['POST'])
def install():
    print(request.json)
    storage.set_value('token', request.json['token'])
    storage.set_value('id', request.json['id'])
    storage.save()

    link_device()
    return '{"status":"OK"}'


@app.route("/status", methods=['GET'])
def status():
    global honkai_token
    status = agent_status.AgentStatus.IDLE

    if honkai_token == b'':
        status = agent_status.AgentStatus.TOKEN_ERROR
    elif system.is_game_running():
        status = agent_status.AgentStatus.GAME_RUNNING

    return {'status': status.value}


def pull_agent_commands():
    requests.get(API_BASE_URL + '/agent', verify=False)


def link_device():
    auth_token = get_honkai_token()
    print(requests.post(API_BASE_URL + '/registration/link', json={"token": auth_token},
                        auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),verify=False))


def init_reg():
    if not storage.has_value('token'):
        webbrowser.open(APP_BASE_URL + '/registration/token')


def get_honkai_token():
    global honkai_token
    req = requests.get(API_BASE_URL + '/agent/pull',
                       auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')), verify=False).text
    print(req)
    with open('temp.ps1', 'w') as temp_file:
        temp_file.write(req)
        temp_file.flush()
    run = subprocess.run('powershell ./temp.ps1', capture_output='stdout')
    url = run.stdout
    honkai_token = url
    os.remove('temp.ps1')
    auth_key = next(filter(lambda f: f[0] == 'authkey', map(lambda x: x.split("="), list(str(url).split("&")))))[1]
    return auth_key


if __name__ == '__main__':
    init_reg()
    app.run(port=25565)
    # t = threading.Thread(target=test)
    # t.start()

init_reg()
