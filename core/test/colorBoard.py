from rgbViews import *
import json

logo = Image.open('res/images/3_bit_test.png').convert('RGB')

class VersionBoard:

    def __init__(self, rootView, defaults=None):
        self.__rootView__ = rootView
        self.rootDir = 'src/core/'
        self.resDir = 'res/'

        # # Views
        # self.versionNum = 21
        # self.versionLabel = RGBLabel(self.__rootView__, 9, 18, "VERSION: " + str(self.versionNum))
        # self.versionLabel.setColor(graphics.Color(0, 255, 255))

        # rootView.__offscreen_canvas__.SetPixel(0, 0, 255, 255, 255)
        # rootView.redraw()

        # self.logo = Image.open(self.resDir + 'images/3_bit_test.png')
        # self.logo = self.logo.convert("RGB")
        self.bootImage = RGBImage(self.__rootView__, 0, 0, logo)


if __name__ == "__main__":
    rootView = RGBBase()
    board = VersionBoard(rootView)
    while True:
        pass