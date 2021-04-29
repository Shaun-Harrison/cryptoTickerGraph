import os

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13b_V3

from data.plot import Plot
from presentation.observer import Observer

SCREEN_HEIGHT = epd2in13b_V3.EPD_WIDTH  # 104
SCREEN_WIDTH = epd2in13b_V3.EPD_HEIGHT  # 212

FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'Roboto-Bold.ttf'), 8)
FONT_LARGE = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'Roboto-Bold.ttf'), 18)

class Epd2in13bv3(Observer):

    def __init__(self, observable, mode):
        super().__init__(observable=observable)
        self.epd = epd2in13b_V3.EPD()

        self.epd.init()
        self.image_black = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        self.image_ry = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)
        self.draw_black = ImageDraw.Draw(self.image_black)
        self.draw_ry = ImageDraw.Draw(self.image_ry)
        self.mode = mode

    def form_image(self, prices):
        self.draw_black.rectangle((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), fill="white")
        screen_draw = self.draw_black
        if self.mode == "candle":
            Plot.candle(prices, size=(SCREEN_WIDTH - 38, 79), position=(35, 0), draw=screen_draw)
        else:
            array_length = len(prices)
            last_element = prices[array_length - 1]
            del prices[-1]
            array_length = len(prices)
            change = prices[array_length - 1]
            del prices[-1]

        Plot.line(prices, size=(SCREEN_WIDTH - 36, 79), position=(36, 0), draw=screen_draw)
        Plot.y_axis_labels(prices, FONT_SMALL, (0, 0), (32, 76), draw=screen_draw)
        #screen_draw.line([(9, 83), (204, 83)])
        screen_draw.line([(30, 3), (30, 80)])
        #screen_draw.line([(51, 87), (51, 101)])
        Plot.caption(prices[len(prices) -1], last_element, change, 82, SCREEN_WIDTH, FONT_LARGE, screen_draw)
    def update(self, data):
        self.form_image(data)
        image_black_rotated = self.image_black.rotate(180)
        image_ry_rotated = self.image_ry.rotate(180)
        self.epd.display(
            self.epd.getbuffer(image_black_rotated),
            self.epd.getbuffer(image_ry_rotated)
        )

    def close(self):
        self.epd.Dev_exit()
