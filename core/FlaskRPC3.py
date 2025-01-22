#!/usr/bin/env python
import json
import rgbmatrix.core
from flask import Flask, request
import sys
import zipfile
import time
import os
from threading import Timer
import traceback
import requests
import threading
import time

# sys.path.append('src/core/views/')
# sys.path.append('src/core/test/')
# sys.path.append('src/wifi/')

from rgbViews import *
from views.baseballBoard import BaseballBoard
from views.soccerBoard import SoccerBoard
from views.lacrosseBoard import LacrosseBoard
from views.footballBoard import FootballBoard
from views.stopwatchBoard import StopwatchBoard
from views.bootBoard import BootBoard
from views.ultimateBoard import UltimateBoard
from views.wrestlingBoard import WrestlingBoard
from views.swimmingBoard import SwimmingBoard
from views.basketballBoard import BasketballBoard
from views.volleyballBoard import VolleyballBoard
from views.versionBoard import VersionBoard
from views.tennisMatchBoard import TennisMatchBoard
from views.clientConnectBoard import ClientConnectBoard
# from connectionManager import *
from core.test.imageBoard import ImageBoard


from PIL import Image


class FlaskRPC:

    def __init__(self):
        self.rootDir = 'src/core/'
        self.rootView = None
        self.board = None
        self.app = self.createApp()
        self.app.debug = False
        self.connMgr = ConnectionManager()

        # image = Image.open('res/images/lederbord_logo_small.png').convert("RGB")
        # print(image)
        # print(image.load())
        # print(image.im.unsafe_ptrs)

        t = threading.Timer(0.1, self.on_start)
        t.start()
        # self.app.run(host='0.0.0.0', port=443, ssl_context=('/usr/src/app/secrets/lederbord_local.cer', '/usr/src/app/secrets/lederbord_local.key'))
        self.app.run(host='0.0.0.0', port=80)


    def on_start(self):
        while True:
            try:
                requests.get('http://127.0.0.1', verify=False)
                return
            except Exception:
                print("Error starting boot board!")
                pass
            
            time.sleep(0.25)

    def createApp(self):
        app = Flask(__name__)

#        @app.after_request
#        def after_request(response):
#            if response.status_code!=200:
#               print(response.status_code)
#               print("client disconnected or request failed")
#               return response
 
        @app.route('/', methods=['GET', 'POST'])
        def hello():
            data = ''
            if request.method == 'GET':
                print("HTTP GET Request")
                data = request.args.get('r', '')
            elif request.method == 'POST':
                print("HTTP post Request")
                if 'r' in request.form:
                    data = request.form['r']
                    print(data)
                else:
                    data = request.data

            # Convert bytes to string if appropriate
            try:
                data = data.decode('utf-8')
            except AttributeError:
                pass

            # Convert data to the json format
            try:
                req = json.loads(data)
            except ValueError:
                return '{"Error":"Could not decode request json"}'

            # Get data from the request
            try:
                method = req['method']
                params = req['params']
                uid = req['id']
            except KeyError:
                return '{"Error":"Missing required entries in request json"}'

            # Call the method
            try:
                # Call the class/obj method is there is a '.'
                if '.' in method:
                    obj = self
                    while '.' in method:
                        # print(method)
                        # print(obj, obj.__dict__)
                        comps = method.split('.')
                        # print(comps[0])
                        obj = getattr(obj, comps[0])
                        method = '.'.join(comps[1:])
                    # print('END OF WHILE', obj, obj.__dict__)
                    resp = getattr(obj, method)(params)
                else:  # Call the local method
                    resp = getattr(self, method)(params)
            except KeyError:
                traceback.print_exc()
                return '{"Error":"Could not find the requested method"}'

            # ret = {"id": uid, "response": resp}
            return '{"id":"%s", "response":%s}' % (uid, resp)

        @app.route('/getProperties/', methods=['GET'])
        def get_properties():
            try:
                with open("/info.json", "r") as in_json:
                    return json.dumps(json.load(in_json))
            except FileNotFoundError:
                return "File Not Found Error"
            except Exception as exception:
                return "Unknown error" + str(exception)

        @app.route('/quit/')
        def quit():
            request.environ.get('werkzeug.server.shutdown')()
            return "Quitting..."

        @app.before_first_request
        def before_first():
            self.createBoot()

        return app

    def start(self, dataStr=None):
        if self.rootView is None:
            self.rootView = RGBBase()
        else:
            self.rootView.removeAllViews()
        return 'Success'

    def createBaseball(self, dataStr=None):
        print(dataStr)
        if self.rootView == None:
            self.start()
        self.clear()
#        print(self)
        print("Create Base ball Method called")
#        self.setBrightness(self,dataStr)
        self.board = BaseballBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createSoccer(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = SoccerBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createFootball(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = FootballBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createLacrosse(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = LacrosseBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createUltimate(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = UltimateBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createWrestling(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = WrestlingBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createSwimming(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = SwimmingBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createBasketball(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = BasketballBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createVolleyball(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = VolleyballBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createVersion(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = VersionBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createStopwatch(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = StopwatchBoard(self.rootView)

    def createTennisMatch(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = TennisMatchBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createTest1(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = TestBoard1(self.rootView, defaults=self.checkParams(dataStr))

    def createClientConnect(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = ClientConnectBoard(self.rootView, dataStr)

    def setClientConnectStatus(self, dataStr=None):
        assert type(self.board) == ClientConnectBoard, "Please start the ClientConnectBoard first!"
        self.board.set_connection_status(dataStr)


    # not used but could be a good recovery method at some point
    def startHotspot(self, dataStr=None):
        self.connMgr.start_hotspot()

    # TODO fix this so that we can modify/create a hotspot file
    # def createHotspot(self, dataStr=None):
    #     params = self.checkParams(dataStr)
    #     if params == None:
    #         return
    #     self.connMgr.create_hotspot(params["ssid"], params["password"])


    def createBoot(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = BootBoard(self.rootView)

    def createImage(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = ImageBoard(self.rootView, defaults=self.checkParams(dataStr))

    def info(self, dataStr=None):
        return "Connected - OLD"

    def checkParams(self, params):
        if type(params) == dict:
            return params
        if type(params) == str:
            try:
                decoded = json.loads(params)
                return decoded
            except json.decoder.JSONDecodeError:
                return None
        else:
            return None

    def getProperties(self, dataStr=None):
        try:
            with open("/home/pi/info.json", "r") as in_json:
                return json.dumps(json.load(in_json))
        except FileNotFoundError:
            return "File Not Found Error"
        except Exception as exception:
            return "Unknown error" + str(exception)

    def clear(self, dataStr=None):
        self.rootView.removeAllViews()

    def setBrightness(self,dataStr):
#        self.rootView.setBrighntess(self.rootView, defaults=self.checkParams(dataStr))
        print("Falsk Brightness")

def keypad_task():
    while True:
        print("Running Keypad Task ...")
        time.sleep(1)

def network_active():
    while True:
        print("Network is active ...")
        time.sleep(1)

if __name__ == '__main__':
    keypad_thread = threading.Thread(target=keypad_task)
    network_thread = threading.Thread(target=network_active)

    # Start the threads
    keypad_thread.start()
    network_thread.start()

    web = FlaskRPC()
    
    # Wait for both threads to finish
    keypad_thread.join()
    network_thread.join()
