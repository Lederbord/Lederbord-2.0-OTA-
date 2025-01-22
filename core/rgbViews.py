import argparse
import time
import sys
import os
import rgbmatrix.core
import threading
from datetime import datetime
from enum import Enum
import subprocess
import json

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image


from BoardInfo import *

class RGBView(object):

    def __init__(self, parent, x , y):
        self.rootDir = 'src/core/'
        self.resDir = 'res/'
        self.__parent__ = parent
        self.__x__ = x
        self.__y__ = y

        self.width = 96
        self.height = 32

    def setOrigin(self, x, y):
        self.__x__ = x
        self.__y__ = y
        self.__parent__.redraw()

    def render(self, matrix, canvas):
        pass


class RGBImage(RGBView):

    def __init__(self, parent, x, y, image):
        super(RGBImage, self).__init__(parent, x, y)
        if type(image) == str:
            # print(image)
            # self.image = Image.open(image).convert('RGB')
            # print(self.image)
            # print(self.image.load())
            # print(self.image.im.unsafe_ptrs)
            raise Exception("Cannot load image from a different thread! Please load the image on start, and pass the image instead.")
        else:
            self.image = image
        self.__parent__.addView(self)
        self.__parent__.redraw()

    def render(self, matrix, canvas):
        matrix.SetImage(self.image, self.__x__, self.__y__)

    def setImage(self, image):
        if type(image) == str:
            # self.image = Image.open(image).convert('RGB')
            raise Exception("Cannot load image from a different thread! Please load the image on start, and pass the image instead.")
        else:
            self.image = image
        self.__parent__.addView(self)
        self.__parent__.redraw()

    #TODO either setPosition() or remove view individually

class TextStyle(Enum):
    FONT = 0
    IMAGE = 1
    IMAGE_RED = 2


class RGBLabel(RGBView):
    # Cache the font's that have already been loaded to reduce load time
    # Key: the file path for the BDF file
    # Value: The graphics.Font() object
    fonts = {}
    bb_green_fonts = []
    bb_red_fonts = []

    @staticmethod
    def LoadFonts():
        # print('[RGBLabel]::LoadFonts')
        assert len(RGBLabel.bb_green_fonts) == 0
        assert len(RGBLabel.bb_red_fonts) == 0
        for i in range(0, 10):
            RGBLabel.bb_green_fonts.append(Image.open('../res/images/bb_' + str(i) + '.png').convert('RGB'))
            RGBLabel.bb_red_fonts.append(Image.open('../res/images/bb_' + str(i) + '_red.png').convert('RGB'))


    # X, Y is at BOTTOM LEFT for draw!!!

    def __init__(self, parent, x, y, text="", textStyle=TextStyle.FONT, font_path="../res/fonts/7x13B.bdf", font_y_offset=10):
        self.__text__ = text
        self.__textStyle__ = textStyle
        self.__color__ = graphics.Color(255, 255, 255)

        if self.__textStyle__ == TextStyle.FONT:
            super(RGBLabel, self).__init__(parent, x, (y + font_y_offset))
            if font_path not in RGBLabel.fonts:
                RGBLabel.fonts[font_path] = graphics.Font()
                RGBLabel.fonts[font_path].LoadFont(font_path)
            self.__font__ = RGBLabel.fonts[font_path]
        elif self.__textStyle__ == TextStyle.IMAGE:
            super(RGBLabel, self).__init__(parent, x, y)
            self.__font__ = RGBLabel.bb_green_fonts
        elif self.__textStyle__ == TextStyle.IMAGE_RED: # for red colors for wrestling board
            super(RGBLabel, self).__init__(parent, x, y)
            self.__font__ = RGBLabel.bb_red_fonts

        self.__parent__.addView(self)
        # self.__parent__.redraw()

    # Fix the bottom left glitch
    def setOrigin(self, x, y):
        if self.__textStyle__ == TextStyle.FONT:
            self.__x__ = x
            self.__y__ = (y + 10)
        else:
            self.__x__ = x
            self.__y__ = y
        self.__parent__.redraw()

    def setText(self, text):
        self.__text__ = text
        self.__parent__.redraw()

    def setColor(self, color):
        self.__color__ = color
        self.__parent__ .redraw()

    def setFont(self, fontURL):
        if fontURL not in RGBLabel.fonts:
            RGBLabel.fonts[fontURL] = graphics.Font()
            RGBLabel.fonts[fontURL].LoadFont(fontURL)
        self.__font__ = RGBLabel.fonts[fontURL]
        self.__parent__.redraw()

    # def transRed(self):
    #     data = np.array(self.__font__[0])
    #     red, green, blue, alpha = data.T
    #     green_areas = (red == 0) & (blue == 0) & (green == 255)
    #     data[..., :-1][green_areas.T] = (255, 0, 0)
    #
    #     self.__font__[0] = Image.fromarray(data)


    def render(self, matrix, canvas):
        # print("[RGBLabel]::render")
        if self.__textStyle__ == TextStyle.FONT:
            graphics.DrawText(self.__parent__.__offscreen_canvas__, self.__font__, self.__x__, self.__y__, self.__color__, self.__text__)
        else:
            w = 17
            for index, char in enumerate(self.__text__):
                i = ord(char) - ord('0')
                if i < 0 or i >= len(self.__font__):
                    print(f"[RBGLabel]::render Invalid char: { i }, __font__: { self.__font__ }, Label.bb_green_fonts: { RGBLabel.bb_green_fonts }, Label.bb_red_fonts: { RGBLabel.bb_red_fonts }")
                    continue
                else:
                    matrix.SetImage(self.__font__[i], self.__x__ + (w*index), self.__y__)

class RGBBase:

    def __init__(self):
        # RGB Matrix Configuration
        self.__options__ = RGBMatrixOptions()
        self.__options__.rows = 16
        self.__options__.cols = 32
        self.__options__.chain_length = 3
        self.__options__.parallel = 3
        self.__options__.brightness = 100
        self.__options__.pwm_bits = 1
        self.__options__.multiplexing = 3
#        self.__options__.row_address_type = 2
#        self.__options__.gpio_slowdown = 0
        self.__options__.pwm_lsb_nanoseconds = 150
        self.__options__.limit_refresh_rate_hz=500
        self.__options__.drop_privileges=0
        self.__options__.show_refresh_rate=1
        # self.__board_info__ = self._getBoardInfo()
        print("Refresh Rate")
        print(self.__options__.show_refresh_rate)

        p_type = os.getenv("LEDERBORD_PANEL_TYPE", '1')
        p_type="3"
        if p_type == "1":
            print("Applying setting for panel type 1")
            self.__options__.multiplexing = 8
            self.__options__.row_address_type = 0
            self.__options__.pwm_lsb_nanoseconds = 90
        elif p_type == "2":
            print("Applying setting for panel type 2")
            self.__options__.multiplexing = 3
            self.__options__.row_address_type = 2
            self.__options__.gpio_slowdown = 2
        elif p_type == "3":
            print("Applying setting for panel type 3")
            self.__options__.multiplexing = 3
            self.__options__.row_address_type = 0
            self.__options__.gpio_slowdown = 2
        else:
            raise Exception("LEDERBORD_PANEL_TYPE env variable must be set to 1, 2, or 3")

        # Create the matrix stuff
        self.__matrix__ = RGBMatrix(options=self.__options__)
        self.__offscreen_canvas__ = self.__matrix__.CreateFrameCanvas()
        self.__offscreen_canvas__.Clear()

        # Create arrays to hold the child views
        self.__children__ = []

    def _getBoardInfo(self):
        board_info = {}
        if(os.path.exists("/info.json")):
            with open("/info.json", "r") as in_json:
                board_info = json.load(in_json)
            return board_info
        else:
            generateInfo() #create file if nonexistent
            return self._getBoardInfo()


    def redraw(self):
        self.__offscreen_canvas__.Clear()

        for child in self.__children__:
            child.render(self.__matrix__, self.__offscreen_canvas__)
        self.__offscreen_canvas__ = self.__matrix__.SwapOnVSync(self.__offscreen_canvas__)

        for child in self.__children__:
            if type(child) != RGBLabel:
                child.render(self.__matrix__, self.__offscreen_canvas__)
            elif (child.__textStyle__ == TextStyle.IMAGE or child.__textStyle__ == TextStyle.IMAGE_RED):
                child.render(self.__matrix__, self.__offscreen_canvas__)

    def addView(self, view):
        self.__children__.append(view)
        self.redraw()

    def removeAllViews(self):
        self.__offscreen_canvas__.Clear()
        self.__children__ = []
        self.redraw()
        print('Removed All View')

    def setBrightness(self, dataStr):
#        self.__matrix__.limit_refresh_rate_hz = int(dataStr)
#        self.__matrix__ = RGBMatrix(options=self.__options__)
        if (int(dataStr) <= 500):
                 self.__options__.limit_refresh_rate_hz = int(dataStr)
        self.__matrix__ = RGBMatrix(options=self.__options__)
        # Clear and redraw the canvas
        self.__offscreen_canvas__ = self.__matrix__.CreateFrameCanvas()
       # self.__offscreen_canvas__.Clear()
        self.redraw()
#        print("rgbmatrix")
        print("Set refresh rate to:", self.__options__.limit_refresh_rate_hz)



class PeriodIndicator:

    def __init__(self, rootView, x, y, letter='P', defPeriod="1"):
        self.__rootView__ = rootView
        self.__x__ = x
        self.__y__ = y
        self.letter = letter
        self.letterLabel = RGBLabel(self.__rootView__, self.__x__, self.__y__, self.letter)
        self.letterLabel.setColor(graphics.Color(255, 255, 0))
        self.numLabel = RGBLabel(self.__rootView__, self.__x__+7, self.__y__, defPeriod)
        #self.numLabel.setColor(graphics.Color(255, 255, 0))

    def setPeriod(self, period):
        self.numLabel.setText(period)


ClockSepImage = Image.open('../res/images/clocksep.png').convert('RGB')
ClockSepImageGreen = Image.open('../res/images/clocksep_green.png').convert('RGB')

class Clock:

    def __init__(self, rootView, x, y, defSeconds="0"):
        self.__rootView__ = rootView
        self.__x__ = x
        self.__y__ = y
        self.rootDir = 'src/core/'
        self.resDir = 'res/'

        stringSeconds = self.parseTime(self.getTimeStr(defSeconds))
        
        self.minLabel = RGBLabel(self.__rootView__, self.__x__, self.__y__, stringSeconds[0],font_path="../res/fonts/10x20B.bdf")
        self.minLabel.setColor(graphics.Color(0, 255, 255))
        self.seperatorImage = RGBImage(self.__rootView__, self.__x__+21, self.__y__-1, ClockSepImage)
        self.secLabel = RGBLabel(self.__rootView__, self.__x__+25, self.__y__, stringSeconds[1],font_path="../res/fonts/10x20B.bdf")
        self.secLabel.setColor(graphics.Color(0, 255, 255))

        self.seconds = int(defSeconds)
        self.format = '%M:%S'
        self.running = False

        self.startTime = None

    def parseTime(self, timeStr):
        return timeStr.split(':')

    def setTime(self, timeStr):
        comps = self.parseTime(timeStr)
        self.minLabel.setText(comps[0])
        self.secLabel.setText(comps[1])
        pass

    def getTimeStr(self, dataStr):
        # return time.strftime(self.format, time.gmtime(dataStr))  # self.seconds
        return "%02d:%02d" % (int(dataStr)/60, int(dataStr)%60)

    def startTimer(self, dataStr=None):
        self.running = True
        self.startTime = datetime.now()
        while self.running:
            elapsed = (datetime.now() - self.startTime).total_seconds()-1
            self.setTime(self.getTimeStr(self.seconds - elapsed))
            time.sleep(0.1)

    def stopTimer(self, dataStr=None):
        self.running = False

    def setSeconds(self, dataStr):
        self.seconds = int(dataStr)
        self.startTime = datetime.now()
        self.setTime(self.getTimeStr(self.seconds))

    def setFormat(self, dataStr):
        self.format = dataStr
        self.setTime(self.getTimeStr())

    def makeGreen(self):
        green = graphics.Color(0, 255, 0)
        self.minLabel.setColor(green)
        self.secLabel.setColor(green)
        self.seperatorImage = RGBImage(self.__rootView__, self.__x__+14, self.__y__+1, ClockSepImageGreen)


RGBLabel.LoadFonts()
