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
# import logging
#import web
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
from views.customText import customText
from BoardInfo import GetWifiConnectionInfo
# from connectionManager import *
from core.test.imageBoard import ImageBoard
#from keypad2 import keypad_module

from PIL import Image

#keypad_interrupt= 10
Score_mode=0
away_score=0
Home_score=0
Inning1=0
Inning2=0
Ball_score=0
Strikes_score=0
Outs_score=0
t=2400
timer_status=0
game_id=0
Half=1
Quarter=1
Down=1
Yards=10
Weight_class=150
H_Set1score=0
H_Set2score=0
H_Set3score=0
G_Set1score=0
G_Set2score=0
G_Set3score=0
Awaywin_score=0
Homewin_score=0
POLL_FREQUENCY_SECS = 3
SHUTDOWN_PIN_NUM = 15
shutdown_cmd = ['sudo', 'shutdown', '-h', '0']
reboot_cmd = ['sudo', 'reboot']

class FlaskRPC:

    def __init__(self):
        self.rootDir = 'src/core/'
        self.rootView = None
        self.board = None
        self.app = self.createApp()
        self.app.debug = False
        self.connMgr = ConnectionManager()
        self.gameid=None
        self.gameinfo=None
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


        # Configure logging to write to a file in the /home/pi/logs directory
  #      log_file = '/home/pi/logs/flask_logs.log'

# Set up basic logging configuration
   #     logging.basicConfig(filename=log_file, level=logging.INFO,
    #                format='%(asctime)s %(levelname)s %(message)s')

# Add a file handler to the Flask app's logger
     #   app.logger.addHandler(logging.FileHandler(log_file))
     #  app.logger.setLevel(logging.INFO)

# You can also log a test message
      #  app.logger.info("Flask server started")

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
                print("HTTP post Request")
                if 'r' in request.form:
                    data = request.form['r']
                    print(data)
                else:
                    data = request.data
                    print(data)

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
                "Id" :self.gameid}
            return jsonify(data)

        @app.route('/resetboard/', methods=['GET'])
        def Set_Reset_Board():
            subprocess.run(reboot_cmd)

        @app.route('/resetGameInfo/', methods=['GET'])
        def Set_Reset_Gameinfo():
            print("Reset Game")
            print(self.gameid)
            global game_id
            global timer_status
            global away_score
            global Home_score
            global Strikes_score
            global Inning1
            global Inning2
            global Ball_score
            global Outs_score
            global Half
            global Quarter
            global Down
            global Yards
            global Weight_class
            global H_Set1score
            global H_Set2score
            global H_Set3score
            global G_Set1score
            global G_Set2score
            global G_Set3score
            global Awaywin_score
            global Homewin_score
            global Score_mode
            global t
            
            if game_id==1: 
               print("Timer Status2400")
               t=2400
            elif game_id==2:
               t=3600
               print("Timer Status3600")
            elif game_id==3:
               t=600
               print("Timer Status-600")
            elif game_id==4 :
               t=600
               print("Timer Status-600")
            elif game_id==5:
               t=2400
               print("Timer Status-2400")
            elif game_id==6:
               t=2400
               print("Timer Status-2400")
            elif game_id==7:
               t=2400
               print("Timer Status-2400")
            elif game_id==9:
               t=600
               print("Timer Status-600")               
            timer_status=0
            away_score=0
            Home_score=0
            Strikes_score=0
            Inning1=0
            Inning2=0
            Ball_score=0
            Outs_score=0
            Half=0
            Quarter=0
            Down=0
            Yards=0
            Weight_class=150
            H_Set1score=0
            H_Set2score=0
            H_Set3score=0
            G_Set1score=0
            G_Set2score=0
            G_Set3score=0
            Awaywin_score=0
            Homewin_score=0
            Score_mode=0
            return "Success", 200



        @app.route('/gameInfo', methods=['GET'])
        def get_Gameinfo():
#            data = ''
            global timer_status
            global away_score
            global Home_score
            global Strikes_score
            global Inning1
            global Inning2
            global Ball_score
            global Outs_score
            global game_id
            global Half
            global Quarter
            global Down
            global Yards
            global Weight_class
            global H_Set1score
            global H_Set2score
            global H_Set3score
            global G_Set1score
            global G_Set2score
            global G_Set3score
            global Awaywin_score
            global Homewin_score
            
            if request.method == 'GET':
                data = request.args.get('Id')                
                print(data)
#                self.GetcurrentGameInfo(data)

                match data:
                   case '1':
                      print("SoccerInfo")
                      print(web.board.Home_score)
                      print(web.board.Away_score)
                      print(web.board.Home_color)
                      print(web.board.Away_color)
                      print(web.board.clock)
                      print(web.board.half)
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      Half=int(web.board.half)                
                      dataStr = {
                              "Id" :"1",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "half":web.board.half,
                              "clock":web.board.clock,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)
                   case '2':

                      print("BaseballInfo")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      print(web.board.Inning)
                      print(web.board.Inning[0])
                      if web.board.Inning[0]=='t':
                         if Inning1<10:
                            Inning1=int(web.board.Inning[1])
                         else:
                            Inning1=int(web.board.Inning[1]+web.board.Inning[2])
                      else:
                         if Inning2<10:
                            Inning2=int(web.board.Inning[1])
                         else:
                            Inning2=int(web.board.Inning[1]+web.board.Inning[2])
                      Ball_score=int(web.board.Balls)
                      Outs_score=int(web.board.Outs)
                      Strikes_score=int(web.board.Strikes)
                      dataStr = {
                              "Id" :"2",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "Inning":web.board.Inning,
                              "Balls":web.board.Balls,
                              "Outs":web.board.Outs,
                              "Strikes":web.board.Strikes,
                              "clock":web.board.clock,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)
                   case '3':

                      print("Football Info")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      Quarter=int(web.board.quarter)
                      Yards=int(web.board.yards)
                      Down=int(web.board.down)
                      dataStr = {
                              "Id" :"3",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "quarters":web.board.quarter,
                              "clock":web.board.clock,
                              "yards":web.board.yards,
                              "downs":web.board.down,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)
                   case '4':
                      print("LacrosseBoard Info")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      Quarter=int(web.board.quarter)
                      dataStr = {
                              "Id" :"4",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "quarters":web.board.quarter,
                              "clock":web.board.clock,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)
                   case '5':
                      print("Basketball Info")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      Half=int(web.board.Period)
                      dataStr = {
                              "Id" :"5",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "Period":web.board.Period,
                              "clock":web.board.clock,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)
                   case '6':
                      print("Volleyball Info")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      Quarter=int(web.board.Period)
                      dataStr = {
                              "Id" :"6",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "Period":web.board.Period,
                              "clock":web.board.clock,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)
                   case '7':
                      print("Wrestling Info")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      Quarter=int(web.board.Period)
                      Weight_class=int(web.board.Weightclass)
                      dataStr = {
                              "Id" :"7",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "Period":web.board.Period,
                              "clock":web.board.clock,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "Weightsclass":web.board.Weightclass,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)


                   case '8':
                      print("Swimming Info")
                      away_score=int(web.board.Heat)
                      Home_score=int(web.board.Event)
                      dataStr = {
                              "Id" :"8",
                              "Heat_score":web.board.Heat,
                              "Event_score":web.board.Event,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)


                   case '9':
                      print("Ultimateboard Info")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      dataStr = {
                              "Id" :"9",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
#                             "half":web.board.half,
                              "clock":web.board.clock,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)


                   case '10':
                      print("Tennismatch Info")
                      if web.board.Away_score=="AD":
                         away_score=web.board.Away_score
                      else:
                         away_score=int(web.board.Away_score)
                      if web.board.Home_score=="AD":
                         Home_score=web.board.Home_score
                      else:
                         Home_score=int(web.board.Home_score)
                      H_Set1score=int(web.board.hs1)
                      H_Set2score=int(web.board.hs2)
                      H_Set3score=int(web.board.hs3)
                      G_Set1score=int(web.board.as1)
                      G_Set2score=int(web.board.as2)
                      G_Set3score=int(web.board.as3)
                      dataStr = {
                              "Id" :"10",
                              "hs1":web.board.hs1,
                              "hs2":web.board.hs2,
                              "hs3":web.board.hs3,
                              "as1":web.board.as1,
                              "as2":web.board.as2,
                              "as3":web.board.as3,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score
                               }
                      return jsonify(dataStr)


                   case '11':
                      print("Pickleball Info")
                      away_score=int(web.board.Away_score)
                      Home_score=int(web.board.Home_score)
                      if web.board.AwayServe[0]=='a':
                         if Inning1<10:
                            Inning1=int(web.board.AwayServe[1])
                         else:
                            Inning1=int(web.board.AwayServe[1]+web.board.AwayServe[2])

                      if web.board.HomeServe[0]=='h':
                         if Inning2<10:
                            Inning2=int(web.board.HomeServe[1])
                         else:
                            Inning2=int(web.board.HomeServe[1]+web.board.HomeServe[2])
#                      Inning1=int(web.board.AwayServe)
#                      Inning2=int(web.board.HomeServe)
                      Awaywin_score=int(web.board.Awaywin_score)
                      Homewin_score=int(web.board.Homewin_score)
                      dataStr = {
                              "Id" :"11",
                              "home_color" : web.board.Home_color,
                              "away_color" : web.board.Away_color,
                              "home_score":web.board.Home_score,
                              "away_score":web.board.Away_score,
                              "away_winscore":web.board.Awaywin_score,
                              "home_winscore":web.board.Homewin_score,
                              "home_serve":web.board.HomeServe,
                              "away_serve":web.board.AwayServe,
                              "current_serve":web.board.CurrentServe,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)

                   case '12':
                      print("Stopwatch Info")
                      dataStr = {
                              "Id" :"12",
                              "clock":web.board.clock,
                              "timerstatus":timer_status}
                      return jsonify(dataStr)

        @app.route('/starttimer/',methods=['GET'])
#        print("Timer_Started")
        def Start_timer():
            print("Timer_Started")
#            data = ''
            global t
            global timer_status
            if request.method == 'GET':
                data = request.args.get('time')
                print(data)
                t=int(data)
            if timer_event.isSet()==0:
                 timer_event.set()
                 timer_status=1
#                timer_start()
                 return "Success", 200




        @app.route('/stoptimer/')
        def Stoptimer():
            global timer_status
            print("Timer Stop command")
            timer_stop()
            timer_status=0
            return "Success", 200


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


    def createSoccer(self, dataStr=None):
        global game_id
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        print(f"=============================ROOT VIEW IS ->>>>> {self.rootView}====================")
        print(f"=============================CHECK PARAMS ->>>>DATA STR {dataStr}====================")
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=1
        Score_mode=0
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        global t
        t= 2400

        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==1:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["half"]=self.gameinfo["half"]
                        dataStr["homeColor"]=defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=1
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]

#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["half"]=self.gameinfo["half"]
                        dataStr["homeColor"]=defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]

#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["half"]=self.gameinfo["half"]
                        dataStr["homeColor"]=defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

        game_id=1
        self.board = SoccerBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createBaseball(self, dataStr=None):
        global game_id
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        global t
        t= 3600
        print(dataStr)
        if self.rootView == None:
            self.start()
        self.clear()
#        print(self)
        print("Create Base ball Method called")
#        self.setBrightness(self,dataStr)
        self.gameid=2
        Score_mode=0
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0

        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==2:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
                        for key in defHome:
                           defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                           defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]

                        dataStr["strikes"]=self.gameinfo["strikes"]
                        dataStr["balls"]=self.gameinfo["balls"]
                        dataStr["outs"]=self.gameinfo["outs"]
                        dataStr["inning"]=self.gameinfo["inning"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                     print("Failed to fetch scores.")
                     dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=2
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]

#                        dataStr["homeScore"] =self.gameinfo["homeScore"]
#                        dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["strikes"]=self.gameinfo["strikes"]
                        dataStr["balls"]=self.gameinfo["balls"]
                        dataStr["outs"]=self.gameinfo["outs"]
                        dataStr["inning"]=self.gameinfo["inning"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                     print("Failed to fetch scores.")
                     dataStr=None
              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["strikes"]=self.gameinfo["strikes"]
                        dataStr["balls"]=self.gameinfo["balls"]
                        dataStr["outs"]=self.gameinfo["outs"]
                        dataStr["inning"]=self.gameinfo["inning"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

#        self.gameid=2
        game_id=2
        self.board = BaseballBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createFootball(self, dataStr=None):
        global t
        global Score_mode
        global game_id
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=3
        Score_mode=0
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        t= 600
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==3:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["downs"]=self.gameinfo["downs"]
                        dataStr["yards"]=self.gameinfo["yards"]
                        dataStr["quarter"]=self.gameinfo["quarter"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=3
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["downs"]=self.gameinfo["downs"]
                        dataStr["yards"]=self.gameinfo["yards"]
                        dataStr["quarter"]=self.gameinfo["quarter"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["downs"]=self.gameinfo["downs"]
                        dataStr["yards"]=self.gameinfo["yards"]
                        dataStr["quarter"]=self.gameinfo["quarter"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=3
        self.board = FootballBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createLacrosse(self, dataStr=None):
        global game_id
        global Score_mode
        global t
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=4
        Score_mode=0
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        t= 600
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==4:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["quarter"]=self.gameinfo["quarter"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=4
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["quarter"]=self.gameinfo["quarter"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["quarter"]=self.gameinfo["quarter"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=4
        self.board = LacrosseBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createBasketball(self, dataStr=None):
        global t
        global game_id
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=5
        Score_mode=0
        t= 2400
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==5:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=5
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=5
        self.board = BasketballBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createVolleyball(self, dataStr=None):
        global t
        global game_id
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=6
        Score_mode=0
        t= 2400
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==6:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=6
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=6
        self.board = VolleyballBoard(self.rootView, defaults=self.checkParams(dataStr))
        
    def createWrestling(self, dataStr=None):
        global t
        global game_id
        global Score_mode
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=7
        Score_mode=0
        t= 2400
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==7:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["weightClass"]=self.gameinfo["weightClass"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=7
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["weightClass"]=self.gameinfo["weightClass"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["period"]=self.gameinfo["period"]
                        dataStr["weightClass"]=self.gameinfo["weightClass"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=7
        self.board = WrestlingBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createSwimming(self, dataStr=None):
        
        global game_id
        global Score_mode
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=8
        Score_mode=0
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==8:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["eventColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["heatColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["eventColor"]= defHome
                        dataStr["heatColor"]= defAway
 
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=8
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["eventColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["heatColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["eventColor"]= defHome
                        dataStr["heatColor"]= defAway
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["eventColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["heatColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["eventColor"]= defHome
                        dataStr["heatColor"]= defAway

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=8
        self.board = SwimmingBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createUltimate(self, dataStr=None):
        global t
        global game_id
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=9
        Score_mode=0
        t= 600
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==9:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                        t=int(self.gameinfo["timeSeconds"])
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=9
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["timeSeconds"]=self.gameinfo["timeSeconds"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=9
        self.board = UltimateBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createTennisMatch(self, dataStr=None):
        t=0
        global game_id
        global Score_mode
        global Set_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=10
        Score_mode=0
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==10:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 

                        if self.gameinfo["homeScore"]=="AD":
                           dataStr["homeScore"]="AD"
                        else:
                           if int(self.gameinfo["homeScore"])<10:
                              dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                           else:
                              dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if self.gameinfo["awayScore"]=="AD":
                           dataStr["awayScore"]="AD"
                        else:
                           if int(self.gameinfo["awayScore"])<10:
                              dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                           else:
                              dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["hs1"]= self.gameinfo["hs1"]
                        dataStr["hs2"]= self.gameinfo["hs2"]
                        dataStr["hs3"]=self.gameinfo["hs3"]
                        dataStr["as1"]= self.gameinfo["as1"]
                        dataStr["as2"]= self.gameinfo["as2"]
                        dataStr["as3"]=self.gameinfo["as3"]
                        print(self.gameinfo["hs1"])
                        if int(self.gameinfo["hs1"])< 7 and int(self.gameinfo["as1"])<7:
                           Score_mode=5
                        elif int(self.gameinfo["hs2"])< 7 and int(self.gameinfo["as2"])<7:
                           Score_mode=6
                        elif int(self.gameinfo["hs3"])< 7 and int(self.gameinfo["as3"])<7:
                           Score_mode=7
 
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=10
                  self.fetch_current_score()
                  if self.gameinfo is not None:

                        if self.gameinfo["homeScore"]=="AD":
                           dataStr["homeScore"]="AD"
                        else:
                           if int(self.gameinfo["homeScore"])<10:
                              dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                           else:
                              dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if self.gameinfo["awayScore"]=="AD":
                           dataStr["awayScore"]="AD"
                        else:
                           if int(self.gameinfo["awayScore"])<10:
                              dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                           else:
                              dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["hs1"]= self.gameinfo["hs1"]
                        dataStr["hs2"]= self.gameinfo["hs2"]
                        dataStr["hs3"]=self.gameinfo["hs3"]
                        dataStr["as1"]= self.gameinfo["as1"]
                        dataStr["as2"]= self.gameinfo["as2"]
                        dataStr["as3"]=self.gameinfo["as3"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:

                        if self.gameinfo["homeScore"]=="AD":
                           dataStr["homeScore"]="AD"
                        else:
                           if int(self.gameinfo["homeScore"])<10:
                              dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                           else:
                              dataStr["homeScore"] =self.gameinfo["homeScore"]
                              
                        if self.gameinfo["awayScore"]=="AD":
                           dataStr["awayScore"]="AD"
                        else:
                           if int(self.gameinfo["awayScore"])<10:
                              dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                           else:
                              dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["hs1"]= self.gameinfo["hs1"]
                        dataStr["hs2"]= self.gameinfo["hs2"]
                        dataStr["hs3"]=self.gameinfo["hs3"]
                        dataStr["as1"]= self.gameinfo["as1"]
                        dataStr["as2"]= self.gameinfo["as2"]
                        dataStr["as3"]=self.gameinfo["as3"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=10
        self.board = TennisMatchBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createPickelBall(self, dataStr=None):
        print("PickelBall called")
        global t
        global game_id
        global Score_mode
        global away_score
        global Home_score
        global Half
        global Inning1
        global Inning2
        if self.rootView == None:
            self.start()
        self.clear()
        self.gameid=11
        Score_mode=0
        away_score=0
        Home_score=0
        Half=0
        Inning1=0
        Inning2=0
        if dataStr is None:
              dataStr = {}
              script_dir = os.path.dirname(os.path.abspath(__file__))
              print(script_dir)
              file_name = f"current_score.txt"
              file_path = os.path.abspath(file_name)
              print(file_path)
              head_tail = os.path.split(file_path)
              print(head_tail)
              if os.path.exists(head_tail[0]+'/Score'):
                 self.fetch_current_score()
                 print("File exists")
                 print(self.gameinfo)
                 print(self.gameinfo["gameid"])
                 print(self.gameid)
                 if int(self.gameinfo["gameid"])==11:
                  print("Game Matched")
                  if self.gameinfo is not None:
                        print("File Matched") 
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])

                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["currentServe"]=self.gameinfo["currentServe"]
                        dataStr["homeServe"]=self.gameinfo["homeServe"]
                        dataStr["awayServe"]=self.gameinfo["awayServe"]
                        if int(self.gameinfo["homewinScore"])<10:
                           dataStr["homewinScore"] ='0'+ self.gameinfo["homewinScore"]
                        else:
                           dataStr["homewinScore"] =self.gameinfo["homewinScore"]
                        if int(self.gameinfo["awaywinScore"])<10:
                           dataStr["awaywinScore"] ='0'+self.gameinfo["awaywinScore"]
                        else:
                           dataStr["awaywinScore"] =self.gameinfo["awaywinScore"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
                 else:
                  print("File Not Matched")
                  script_dir = os.path.dirname(os.path.abspath(__file__))
                  print(script_dir)
                  file_name = f"current_score.txt"
                  file_path = os.path.abspath(file_name)
                  print(file_path)
                  head_tail = os.path.split(file_path)
                  path=head_tail[0]+'/Score'
                  file_path1=os.path.join(path, file_name)
                  os.remove(file_path1)
                  self.gameid=11
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])
                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["currentServe"]=self.gameinfo["currentServe"]
                        dataStr["homeServe"]=self.gameinfo["homeServe"]
                        dataStr["awayServe"]=self.gameinfo["awayServe"]
                        if int(self.gameinfo["homewinScore"])<10:
                           dataStr["homewinScore"] ='0'+ self.gameinfo["homewinScore"]
                        else:
                           dataStr["homewinScore"] =self.gameinfo["homewinScore"]
                        if int(self.gameinfo["awaywinScore"])<10:
                           dataStr["awaywinScore"] ='0'+self.gameinfo["awaywinScore"]
                        else:
                           dataStr["awaywinScore"] =self.gameinfo["awaywinScore"]
                  else:
                        print("Failed to fetch scores.")
                        dataStr=None

              else:
                  print("The file does not exist")
                  self.fetch_current_score()
                  if self.gameinfo is not None:
                        defHome={}
                        defHome=json.loads(self.gameinfo["homeColor"])
#                    print(defHome["R"])
                        for key in defHome:
                          defHome[key] = int(defHome[key])
                        defAway={}
                        defAway=json.loads(self.gameinfo["awayColor"])

                        for key in defAway:
                          defAway[key] = int(defAway[key])
                        if int(self.gameinfo["homeScore"])<10:
                           dataStr["homeScore"] ='0'+ self.gameinfo["homeScore"]
                        else:
                           dataStr["homeScore"] =self.gameinfo["homeScore"]
                        if int(self.gameinfo["awayScore"])<10:
                           dataStr["awayScore"] ='0'+self.gameinfo["awayScore"]
                        else:
                           dataStr["awayScore"] =self.gameinfo["awayScore"]
#                        dataStr["homeScore"] = self.gameinfo["homeScore"]
#                        dataStr["awayScore"] = self.gameinfo["awayScore"]
                        dataStr["homeColor"]= defHome
                        dataStr["awayColor"]= defAway
                        dataStr["currentServe"]=self.gameinfo["currentServe"]
                        dataStr["homeServe"]=self.gameinfo["homeServe"]
                        dataStr["awayServe"]=self.gameinfo["awayServe"]
                        if int(self.gameinfo["homewinScore"])<10:
                           dataStr["homewinScore"] ='0'+ self.gameinfo["homewinScore"]
                        else:
                           dataStr["homewinScore"] =self.gameinfo["homewinScore"]
                        if int(self.gameinfo["awaywinScore"])<10:
                           dataStr["awaywinScore"] ='0'+self.gameinfo["awaywinScore"]
                        else:
                           dataStr["awaywinScore"] =self.gameinfo["awaywinScore"]

                  else:
                        print("Failed to fetch scores.")
                        dataStr=None
        game_id=11
        self.board = PickelBallBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createVersion(self, dataStr=None):
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = VersionBoard(self.rootView, defaults=self.checkParams(dataStr))

    def createStopwatch(self, dataStr=None):
        global game_id
        print(game_id)
        t=0
        if self.rootView == None:
            self.start()
        self.clear()
        self.board = StopwatchBoard(self.rootView)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(script_dir)
        file_name = f"current_score.txt"
        directory_path = os.path.join(script_dir, "Score")
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path,file_name)
        print(file_path)
        print("Game ID Value")
        # Check if the file exists; create it if it doesn't
        if not os.path.exists(file_path):
          pass
        else:
          os.remove(file_path)
          pass
        self.gameid=12
        game_id=12
     


    def createCustomText(self,dataStr=None):
        print("Custom Text Function")
        if self.rootView == None:
           self.start()
        self.clear()
#        print(self)
        print("Create Base ball Method called")
#        self.setBrightness(self,dataStr)
        self.gameid=13
        game_id=13
        self.board = customText(self.rootView, defaults=self.checkParams(dataStr))



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

    def fetch_current_score(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(script_dir)
        file_name = f"current_score.txt"
        directory_path = os.path.join(script_dir, "Score")
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path,file_name)
        print(file_path)
        print("Game ID Value")
        print(self.gameid)
        # Check if the file exists; create it if it doesn't
        if not os.path.exists(file_path):
          try:
            match self.gameid:
              case 1:
               print("Soccer defaults")
               defaults = {
                   "gameid":"1",
                   "homeScore": "0",
                   "awayScore": "0",
                   "half": "1",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "2400"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])

              case 2:
               print("Base ball  file creation")
               defaults = {
                   "gameid":"2",
                   "homeScore": "0",
                   "awayScore": "0",
                   "balls": "0",
                   "strikes": "0",
                   "outs": "0",
                   "inning": "b1",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "3600"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])
              case 3:
               print("Football  file creation")
               defaults = {
                   "gameid":"3",
                   "homeScore": "0",
                   "awayScore": "0",
                   "downs": "1",
                   "yards": "10",
                   "quarter": "1",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "600"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])
              case 4:
               print("LacrosseBoard ball  file creation")
               defaults = {
                   "gameid":"4",
                   "homeScore": "0",
                   "awayScore": "0",
                   "quarter": "1",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "600"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])
              case 5:
               print("Basketball  file creation")
               defaults = {
                   "gameid":"5",
                   "homeScore": "0",
                   "awayScore": "0",
                   "period": "1",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "2400"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])
              case 6:
               print("Volleyball  file creation")
               defaults = {
                   "gameid":"6",
                   "homeScore": "0",
                   "awayScore": "0",
                   "period": "1",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "2400"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])
              case 7:
               print("wrestlingBoard  file creation")
               defaults = {
                   "gameid":"7",
                   "homeScore": "0",
                   "awayScore": "0",
                   "weightClass": "150",
                   "period": "1",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "2400"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])
              case 8:
               print("swimmingBoard  file creation")
               defaults = {
                   "gameid":"8",
                   "homeScore": "0",
                   "awayScore": "0",
                   "eventColor": {"R": "0", "G": "255", "B": "255"},
                   "heatColor": {"R": "0", "G": "255", "B": "255"}
                  }
               defaults["eventColor"]=json.dumps(defaults["eventColor"])
               defaults["heatColor"]=json.dumps(defaults["heatColor"])
              case 9:
               print("ultimateBoard ball  file creation")
               defaults = {
                   "gameid":"9",
                   "homeScore": "0",
                   "awayScore": "0",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "timeSeconds": "600"
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])
              case 10:
               print("Tennis  file creation")
               defaults = {
                   "gameid":"10",
                   "homeScore": "0",
                   "awayScore": "0",
                   "hs1": "0",
                   "hs2": "0",
                   "hs3": "0",
                   "as1": "0",
                   "as2": "0",
                   "as3": "0"
                  }
              case 11:
               print("PickelBall  file creation")
               defaults = {
                   "gameid":"11",
                   "homeScore": "0",
                   "awayScore": "0",
                   "homeColor": {"R": "0", "G": "255", "B": "255"},
                   "awayColor": {"R": "0", "G": "255", "B": "255"},
                   "homeServe": "h0",
                   "awayServe": "a0",
                   "currentServe":"00",
                   "awaywinScore": "00",
                   "homewinScore": "00",
                  }
               defaults["homeColor"]=json.dumps(defaults["homeColor"])
               defaults["awayColor"]=json.dumps(defaults["awayColor"])



            with open(file_path, 'w+') as f:
               f.write(json.dumps(defaults))
          except IOError as e:
             print(f"Error creating file '{file_path}': {e}")
        else:
           print(f"File '{file_path}' already exists.")  
        try:
#           soccer_score = subprocess.check_output(f"cat {file_path}",shell=True).rstrip().decode()
#           if '\t' in soccer_score:
#              home_score = soccer_score.split('\t')[0]
#              away_score = soccer_score.split('\t')[1]
#              print(f"Current Home Score -> {home_score}")
#              print(f"Current Away Score -> {away_score}")
#              return home_score, away_score
            home_score = None
            away_score = None
            with open(file_path, 'r+') as file:
             first_char = file.read(1)
             print(file.tell())
             file.seek(0)
             print("First Character")
             print(first_char)
             print(file.tell())
             if first_char=='' or first_char==None:
                print("File is empty")
                os.remove(file_path)
                print("File Deleted")
                try:
                    match self.gameid:
                      case 1:
                       print("Soccer defaults")
                       defaults = {
                           "gameid":"1",
                           "homeScore": "0",
                           "awayScore": "0",
                           "half": "1",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])

                      case 2:
                       print("Base ball  file creation")
                       defaults = {
                           "gameid":"2",
                           "homeScore": "0",
                           "awayScore": "0",
                           "balls": "0",
                           "strikes": "0",
                           "outs": "0",
                           "inning": "b1",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])
                      case 3:
                       print("Football  file creation")
                       defaults = {
                           "gameid":"3",
                           "homeScore": "0",
                           "awayScore": "0",
                           "downs": "1",
                           "yards": "10",
                           "quarter": "1",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])
                      case 4:
                       print("LacrosseBoard ball  file creation")
                       defaults = {
                           "gameid":"4",
                           "homeScore": "0",
                           "awayScore": "0",
                           "quarter": "1",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])
                      case 5:
                       print("Basketball  file creation")
                       defaults = {
                           "gameid":"5",
                           "homeScore": "0",
                           "awayScore": "0",
                           "period": "1",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])
                      case 6:
                       print("Volleyball  file creation")
                       defaults = {
                           "gameid":"6",
                           "homeScore": "0",
                           "awayScore": "0",
                           "period": "1",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])
                      case 7:
                       print("wrestlingBoard  file creation")
                       defaults = {
                           "gameid":"7",
                           "homeScore": "0",
                           "awayScore": "0",
                           "weightClass": "150",
                           "period": "1",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])
                      case 8:
                       print("swimmingBoard  file creation")
                       defaults = {
                           "gameid":"8",
                           "homeScore": "0",
                           "awayScore": "0",
                           "eventColor": {"R": "0", "G": "255", "B": "255"},
                           "heatColor": {"R": "0", "G": "255", "B": "255"}
                          }
                       defaults["eventColor"]=json.dumps(defaults["eventColor"])
                       defaults["heatColor"]=json.dumps(defaults["heatColor"])
                      case 9:
                       print("ultimateBoard ball  file creation")
                       defaults = {
                           "gameid":"9",
                           "homeScore": "0",
                           "awayScore": "0",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "timeSeconds": "0"
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])
                      case 10:
                       print("Tennis  file creation")
                       defaults = {
                           "gameid":"10",
                           "homeScore": "0",
                           "awayScore": "0",
                           "hs1": "0",
                           "hs2": "0",
                           "hs3": "0",
                           "as1": "0",
                           "as2": "0",
                           "as3": "0"
                          }
                      case 11:
                       print("PickelBall  file creation")
                       defaults = {
                           "gameid":"11",
                           "homeScore": "0",
                           "awayScore": "0",
                           "homeColor": {"R": "0", "G": "255", "B": "255"},
                           "awayColor": {"R": "0", "G": "255", "B": "255"},
                           "homeServe": "h0",
                           "awayServe": "a0",
                           "currentServe":"00",
                           "awaywinScore": "00",
                           "homewinScore": "00",
                          }
                       defaults["homeColor"]=json.dumps(defaults["homeColor"])
                       defaults["awayColor"]=json.dumps(defaults["awayColor"])



                    with open(file_path, 'w+') as f:
                       f.write(json.dumps(defaults))
                    with open(file_path, 'r+') as f:
                       score=f.read()
                       self.gameinfo=json.loads(score)
                       self.gameid=self.gameinfo["gameid"]
                       return self.gameinfo

                except IOError as e:
                     print(f"Error creating file '{file_path}': {e}")
             else:
              score=file.read()
              print("File read")
              self.gameinfo=json.loads(score)
              print(self.gameinfo["gameid"])
              self.gameid=self.gameinfo["gameid"]
              print(self.gameid)
              print(type(self.gameinfo))
#              home_score=data["homeScore"]
#              away_score=data["awayScore"]
#              for line in file:
#                line = line.strip()  # Remove leading/trailing whitespace and newline characters

                # Check if the line starts with "Home:" or "Away:"
#                if line.startswith("homeScore:"):
#                    home_score = line.split(":")[1].strip()  # Extract score after "Home:"
#                elif line.startswith("awayScore:"):
#                   away_score = line.split(":")[1].strip()  # Extract score after "Away:"
#              print(home_score)
#              print(away_score)
                # If both scores are found, no need to continue
              if self.gameinfo["gameid"] is not None :
                  print("Scores of current game")
                  print(self.gameinfo)
                  return self.gameinfo
              else:
                  print("Invalid format: File content does not contain tab-separated scores.")
                  return self.gameinfo
        except subprocess.CalledProcessError as e:
           print(f"Error: {e}")
           return None
        except Exception as e:
           print(f"Error: {e}")
           return None  # Return None for other unexpected errors
    pass

# define the countdown func. 
def countdown(timer_event):
    global t
    global timer_status  
    global game_id 
    while True:
       print("Countdown task running")
       timer_event.wait()
       while t:
          mins, secs = divmod(t, 60)
          timer = '{:02d}:{:02d}'.format(mins, secs)
          print(timer, end="\r")
          print("countdown task")
          print("Countdown-GameID")
          print(game_id) 
#        print(timer_status)
          if timer_event.isSet():
             print("Timer Set")
             obj = web.board
             method ='setClock'
             timer_status=1
             params=timer
             resp = getattr(obj, method)(params)
             time.sleep(1)
             t -= 1
          else:
             timer_status=0
             print("Timer Stopped")
             timer_event.wait()

       if timer_event.isSet():
          if t==0:
             mins, secs = divmod(t, 60)
             timer = '{:02d}:{:02d}'.format(mins, secs)
             obj = web.board
             method ='setClock'
             params=timer
             resp = getattr(obj, method)(params)
             print("Timer Expired")
#             keypad.output_enable()
             time.sleep(5)
 #            keypad.output_disable()
             timer_event.clear()
             timer_status=0
 




# input time in seconds

def timer_start():
    print("Timer started")
    if timer_event.isSet()==0:
       timer_event.set()

def timer_stop():
    print("Timer stop")
    timer_event.clear()

def update_mode_color():
    obj = web.board
    method = 'setModeButtonColor'
    
    colors = {
        0: {"R": "255", "G": "0", "B": "0"},  # Red for Away Score mode
        1: {"R": "0", "G": "0", "B": "255"},  # Blue for Home Score mode
        2: {"R": "0", "G": "255", "B": "0"}   # Green for Timer mode
    }
    
    color = colors.get(Score_mode, {"R": "0", "G": "0", "B": "0"})  # Default to black if mode not found
    resp = getattr(obj, method)(json.dumps(color))
    print(f"Mode Button Color updated to: {color}")



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
        


def Shutdowntask(event):
    while True:
        event.wait()
        print("Shutdown Loop Running")     
        value = GPIO.input(SHUTDOWN_PIN_NUM)
        print(value)
#        debug_print("Read {} from pin {}".format(value, SHUTDOWN_PIN_NUM))
        if int(value) == 1:
#            debug_print("HI was detected on pin {}. Shutting down...".format(SHUTDOWN_PIN_NUM))
            # value_file.close()
            print("Pi shutdown start")
            print("Shutdown is running")
            shutdown_pi()
            print("Shutdown complete")
#        time.sleep(POLL_FREQUENCY_SECS)
        time.sleep(3)

def shutdown_pi():  
    print("Performing Shutdown")
    if timer_event.isSet()==1:
       timer_event.clear()
    subprocess.run(shutdown_cmd)
#    exit(0)

if __name__ == '__main__':
 
    GPIO.setmode(GPIO.BCM)
#    GPIO.setup(keypad_interrupt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHUTDOWN_PIN_NUM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#    GPIO.add_event_detect(keypad_interrupt,GPIO.FALLING,callback=button_pressed_callback, bouncetime=100)
    
    timer_status=0
 #   keypad= keypad_module(0x27,0,0)
 #  keypad.keyvalue=0
 #  keypad.value= keypad.getch()
    web = FlaskRPC()
    event=threading.Event()
    timer_event = threading.Event()
 #  keypad_thread = threading.Thread(target=keypad_task,args=(event,))
    network_thread = threading.Thread(target=network_active)
    clients_thread = threading.Thread(target=fetch_associated_clients)
    shutdown_thread =threading.Thread(target=Shutdowntask,args=(event,))   
    timer_thread = threading.Thread(target=countdown,args=(timer_event,))
    # Start the threads
 #   keypad_thread.start()
    network_thread.start()
    shutdown_thread.start()
    clients_thread.start()
    timer_thread.start()
    
#    web = FlaskRPC()
    web.app_run()
#    event.set()
    fetch_current_score()
    
    # Wait for both threads to finish
 #  keypad_thread.join()
    network_thread.join()
    shutdown_thread.join()
    clients_thread.join()
    timer_thread.join()
    
