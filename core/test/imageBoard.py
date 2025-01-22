import sys

# sys.path.append('src/core/')

from PIL import Image
from rgbViews import *
from rgbmatrix import graphics
from BoardInfo import GetWifiInfo, GetWifiConnectionInfo

# TODO allow image via multipart upload


class ImageBoard:
    def __init__(self, rootView, defaults=None):
        if defaults is None:
            # set default values here
            defaults = {
                "filename": "lederbord_logo_small.png",
                "rotate": "0",
                "x": 0,
                "y": 0,
                "flipLR": 0,
                "flipTB": 0
            }

        rotate_dict = {"0": Image.NONE,
                       "90": Image.ROTATE_90,
                       "180": Image.ROTATE_180,
                       "270": Image.ROTATE_270}

        self.rootDir = 'src/core/'
        self.resDir = 'res/'
        self.__rootView__ = rootView
        self.image = Image.open(self.resDir + 'images/' + defaults["filename"])
        self.image = self.image.convert("RGB")
        if defaults["rotate"] != "0":
            self.image = self.image.transpose(rotate_dict[defaults["rotate"]])
        if defaults["flipLR"]:
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        if defaults["flipTB"]:
            self.image = self.image.transpose(Image.FLIP_TOP_BOTTOM)
        self.imageView = RGBImage(self.__rootView__, defaults["x"], defaults["y"], self.image)


if __name__ == "__main__":
    root = RGBBase()
    boot = ImageBoard(root)
    while True:
        pass
