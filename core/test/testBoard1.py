from rgbViews import *
import json


class TestBoard1:



    def __init__(self, rootView, defaults=None):
        self.__rootView__ = rootView

        self.led_map = [[0, 0], [32, 0], [64, 0],
                        [0, 16], [32, 16], [64, 16],
                        [0, 32], [32, 32], [64, 32]]

        if defaults==None:
            #set default values here
            defaults = {
                "1": {
                    "R": 255,
                    "G": 255,
                    "B": 0,
                    "Bright": 100
                },
                "3": {
                    "R": 255,
                    "G": 0,
                    "B": 255,
                    "Bright": 100
                },
                "5": {
                    "R": 0,
                    "G": 255,
                    "B": 255,
                    "Bright": 100
                },
                "7": {
                    "R": 255,
                    "G": 0,
                    "B": 255,
                    "Bright": 100
                },
                "9": {
                    "R": 255,
                    "G": 255,
                    "B": 0,
                    "Bright": 100
                }
            }

        self.defaults = defaults



        rootView.addView(self)

    def render(self, matrix, canvas):
        for key in self.defaults.keys():
            int_key = int(key) - 1
            bright = self.defaults[key]["Bright"]
            red = (self.defaults[key]["R"] * bright) // 100
            green = (self.defaults[key]["G"] * bright) // 100
            blue = (self.defaults[key]["B"] * bright) // 100
            for i in range(0, 32):
                for j in range(0, 16):
                    canvas.SetPixel(self.led_map[int_key][0]+i,self.led_map[int_key][1]+j, red, green, blue)




    #     # Views
    #     self.awayLabel = RGBLabel(self.__rootView__, 0, 0, "GUEST")
    #     self.awayScore = RGBLabel(self.__rootView__, 0, 12, defaults["awayScore"], TextStyle.IMAGE)
    #     self.homeLabel = RGBLabel(self.__rootView__, 63, 0, "HOME")
    #     self.homeScore = RGBLabel(self.__rootView__, 60, 12, defaults["homeScore"], TextStyle.IMAGE)
    #     defAway = defaults["awayColor"]
    #     defHome = defaults["homeColor"]
    #     self.awayLabel.setColor(graphics.Color(defAway["R"], defAway["G"], defAway["B"]))
    #     self.homeLabel.setColor(graphics.Color(defHome["R"], defHome["G"], defHome["B"]))
    #     self.clockIndicator = Clock(self.__rootView__, 33, 38, defSeconds=defaults['timeSeconds'])
    #     self.periodIndicator = PeriodIndicator(self.__rootView__, 43, 0, 'Q', defPeriod=defaults['quarter'])
    #
    # def setHomeScore(self, dataStr):
    #     # TODO make app send correct data instead of fixing here
    #     if len(dataStr) == 1:
    #         self.homeScore.setText("0" + dataStr)
    #     else:
    #         self.homeScore.setText(dataStr)
    #
    # def setHomeColor(self, dataStr):
    #     colorObject = json.loads(dataStr)
    #     red = int(colorObject["R"])
    #     green = int(colorObject["G"])
    #     blue = int(colorObject["B"])
    #     self.homeLabel.setColor(graphics.Color(red, green, blue))
    #
    # def setAwayScore(self, dataStr):
    #     # TODO make app send correct data instead of fixing here
    #     if len(dataStr) == 1:
    #         self.awayScore.setText("0" + dataStr)
    #     else:
    #         self.awayScore.setText(dataStr)
    #
    # def setAwayColor(self, dataStr):
    #     colorObject = json.loads(dataStr)
    #     red = int(colorObject["R"])
    #     green = int(colorObject["G"])
    #     blue = int(colorObject["B"])
    #     self.awayLabel.setColor(graphics.Color(red, green, blue))
    #
    # def setClock(self, dataStr):
    #     self.clockIndicator.setTime(dataStr)
    #
    # def setQuarter(self, dataStr):
    #     self.periodIndicator.setPeriod(dataStr)

if __name__ == "__main__":
    rootView = RGBBase()
    board = TestBoard1(rootView)
    while True:
        pass