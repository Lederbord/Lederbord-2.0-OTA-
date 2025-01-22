#!/usr/bin/env python
import json
import rgbmatrix.core
from flask import Flask, request,jsonify
import sys
import zipfile
import time
import os
from threading import Timer
import traceback
import requests
import threading
import time
import subprocess
import re
import RPi.GPIO as GPIO
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
from views.pickleballBoard import PickelBallBoard
# from connectionManager import *
from core.test.imageBoard import ImageBoard
from keypad2 import keypad_module

from PIL import Image

keypad_interrupt= 10
Score_mode=0
away_score=0
Home_score=0

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
#        self.app.run(host='0.0.0.0', port=80)


    def on_start(self):
        while True:
            try:
                requests.get('http://127.0.0.1', verify=False)
                return
            except Exception:
                print("Error starting boot board!")
                pass

            time.sleep(0.25)

    def app_run(self):
        self.app.run(host='0.0.0.0', port=80)


    def createApp(self):
        app = Flask(__name__)

#        @app.after_request
#        def after_request(response):
#            if response.status_code!=200:
#               print(response.status_code)
#               print("client disconnected or request failed")
#               return response


        def init_app():
            print("This function will run once before the first request.")
            self.createBoot()


        with app.app_context():
            init_app()

 
        @app.route('/', methods=['GET', 'POST'])
        def hello():
            event.set()
            data = ''
            if request.method == 'GET':
                print("HTTP GET Request")
                data = request.args.get('r', '')
                print(data)
            elif request.method == 'POST':
                #print("HTTP post Request")
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
                        print(method)
#                        print(obj, obj.__dict__)
                        comps = method.split('.')
                        print(comps[0])
                        obj = getattr(obj, comps[0])
                        method = '.'.join(comps[1:])
#                    print('END OF WHILE', obj, obj.__dict__)
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



        @app.route('/ping/', methods=['GET'])
        def get_connectivity():
            return "Success", 200

        @app.route('/currentGameInfo/', methods=['GET'])
        def get_Current_Gameinfo():
#            print(web.board)
            data = {
                "Id" :"1"}
            return jsonify(data)

        @app.route('/gameInfo', methods=['GET'])
        def get_Gameinfo():
#            data = ''
            if request.method == 'GET':
                data = request.args.get('Id')                
#                print(data)
#                self.GetcurrentGameInfo(data)
                print(web.board.Home_score)
                print(web.board.Away_score)
                print(web.board.Home_color)
                print(web.board.Away_color)
                print(web.board.clock)
                print(web.board.half)
                dataStr = {
                        "Id" :"1",
                        "home_color" : web.board.Home_color,
                        "away_color" : web.board.Away_color,
                        "half":web.board.half,
                        "clock":web.board.clock,
                        "home_score":web.board.Home_score,
                        "away_score":web.board.Away_score}
                return jsonify(dataStr)

        @app.route('/quit/')
        def quit():
            request.environ.get('werkzeug.server.shutdown')()
            return "Quitting..."

#        @app.before_first_request
#        def before_first():
#            self.createBoot()

        return app

    def GetcurrentGameInfo(self,dataStr):
        print("GameId")
        obj=web.board
#        print(obj.homeScore)
#        print(self.board.homeScore)
        if dataStr==1:
#            case 1:
           print("Case1")
           dataStr = {
                        "Id" :"1",
                        "home_label" : self.board.homeLabel,
                        "home_color" : self.board.defHome,
                        "away_label" : self.board.awayLabel,
                        "away_color" : self.board.defAway,
                        "half":self.board.halfIndicator,
                        "clock":self.board.clockIndicator,
                        "home_score":self.board.homeScore,
                        "away_score":self.board.awayScore}
           print(dataStr)
        return dataStr




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
        print(f"=============================ROOT VIEW IS ->>>>> {self.rootView}====================")
        print(f"=============================CHECK PARAMS ->>>>DATA STR {dataStr}====================")
        if self.rootView == None:
            self.start()
        self.clear()
        if dataStr is None:
            dataStr = {}
            home_score, away_score = self.fetch_current_score(game_type="soccer")
            dataStr["homeScore"] = home_score
            dataStr["awayScore"] = away_score
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

    def createPickelBall(self, dataStr=None):
        print("PickelBall called")
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = PickelBallBoard(self.rootView, defaults=self.checkParams(dataStr))

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


    def setAwaywinscore(self, dataStr=None):
        print("Flask server method called")

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
        #return 
        self.rootView.removeAllViews()

    def setBrightness(self,dataStr):
#        self.rootView.setBrighntess(self.rootView, defaults=self.checkParams(dataStr))
        print("Falsk Brightness")

    def fetch_current_score(self, game_type=""):
        soccer_score = subprocess.check_output(f"cat /tmp/current_score_{game_type}",shell=True).rstrip().decode()
        home_score = soccer_score.split('\t')[0]
        away_score = soccer_score.split('\t')[1]
        print(f"Current Home Score -> {home_score}")
        print(f"Current Away Score -> {away_score}")
        return home_score, away_score
    pass

# define the countdown func. 
def countdown(t,timer_event): 

    timer_event.wait()
    print(t)
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        print("countdown task")
#        print(timer_status)
        if timer_event.isSet():
           obj = web.board
           method ='setClock'
#        away_score= getattr(obj,'awayScore')
#        print("Current score")
#        print(away_score)
           params=timer
           resp = getattr(obj, method)(params)
           time.sleep(1)
           t -= 1
        else:
#           timer_status=0
           print("Timer Stopped")
           timer_event.wait()

#           break
#    print('Timer stopped')
#    timer_status=0


# input time in seconds
t = 2400

def timer_start():
    print("Waiting for Keypad Event")
    timer_event.wait()
    print("Timer started")
#    t =2400
    if timer_event.isSet():
       timer_status=1
       countdown(t,timer_status)

def timer_stop():
    print("Timer stop")
    timer_status=0
#    countdown(t,timer_status)
    timer_event.clear()

def keypad_task(event):
    global Score_mode
    global away_score
    global Home_score
    while True:
        print("Running Keypad Task ...")
        event.wait()
        keypad.keyvalue=keypad.getch()
        print(keypad.keyvalue)
        if keypad.keyvalue !=0:
#           change_score()
          obj = web.board
          match keypad.keyvalue:
             case 1:
#          obj = getattr(obj,board)
                 if Score_mode==0:
                    method ='setAwayScore'
                    print(away_score)
                    if away_score<99:
                       away_score=away_score+1
                       params=str(away_score)
                       resp = getattr(obj, method)(params)

                 else:
                    method ='setHomeScore'
#                 away_score= obj.awayScore
                    print(Home_score)
                    if Home_score<99:
                       Home_score=Home_score+1
                       params=str(Home_score)
                       resp = getattr(obj, method)(params)


             case 2:

                 if Score_mode==0:
                    method ='setAwayScore'
                    print(away_score)
                    if away_score>0:
                       away_score=away_score-1
                       params=str(away_score)
                       resp = getattr(obj, method)(params)
                 else:
                    method ='setHomeScore'
#                 away_score= getattr(obj,'awayScore')
                    print("Current score")
                    print(Home_score)
                    if Home_score>0:
                       Home_score=Home_score-1
                       params=str(Home_score)
                       resp = getattr(obj, method)(params)
             case 4:
#                 method ='setClock'
#                 away_score= getattr(obj,'awayScore')
#                 print("Current score")
#                 print(away_score)
#                 params='20:00'
#                 resp = getattr(obj, method)(params)
#                  timer_status=1
                  print("Timer Start key Pressed")
                  if timer_event.isSet()==0:
                     timer_event.set()
                  else:
                     timer_event.clear()
             case 8:
                  print("Player Slection Key Pressed")
#                  timer_status=0
                  if Score_mode==0:
                     Score_mode=1
                  else:
                     Score_mode=0

#                  timer_start(timer_event)
#                  timer_status=0 
#                 method ='setClock'
#                 away_score= getattr(obj,'awayScore')
#                 print("Current score")
#                 print(away_score)
#                 params='10:00'
#                 resp = getattr(obj, method)(params)

#          if keypad.keyvalue ==1:
#             params='1'
#          else:
#             params='2'
#          resp = getattr(obj, method)(params)
#          away_score=board.awayScore
#          away_score=away_score+1
#          self.board.setAwayScore(board,away_score)
        time.sleep(1)

def change_score():
          obj = web.board
#          obj = getattr(obj,board)
          method =setAwayScore
          away_score= getattr(obj,awayScore)
          params=away_score+1
          resp = getattr(obj, method)(params)



def network_active():
    while True:
        print("Network is active ...")
        time.sleep(1)

def fetch_associated_clients():
    while True:
        #print("List of associated clients")
        sta_dump = subprocess.check_output("iw dev wlan0 station dump",shell=True).rstrip().decode()
        match = re.compile(r"Station (.+) \(on wlan0\)")
        sta_mac_addresses = match.findall(sta_dump)
        #print(sta_mac_addresses)
        time.sleep(1)
        
def button_pressed_callback(channel):
    print("Button pressed!")
    keypad.keyvalue=keypad.getch()
    print(keypad.keyvalue)


if __name__ == '__main__':
 
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(keypad_interrupt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#    GPIO.add_event_detect(keypad_interrupt,GPIO.FALLING,callback=button_pressed_callback, bouncetime=100)
    
    global timer_status
    keypad= keypad_module(0x27,0,0)
    keypad.keyvalue=0
    keypad.value= keypad.getch()
    web = FlaskRPC()
    event=threading.Event()
    keypad_thread = threading.Thread(target=keypad_task,args=(event,))
    network_thread = threading.Thread(target=network_active)
    clients_thread = threading.Thread(target=fetch_associated_clients)

    timer_event = threading.Event()
    timer_thread = threading.Thread(target=countdown,args=(t,timer_event,))
    # Start the threads
    keypad_thread.start()
    network_thread.start()
    clients_thread.start()
    timer_thread.start()
#    web = FlaskRPC()
    web.app_run()
#    event.set()
    fetch_current_score()

    # Wait for both threads to finish
    keypad_thread.join()
    network_thread.join()
    clients_thread.join()
    timer_thread.join()
