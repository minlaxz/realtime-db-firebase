from luma.oled.device import sh1106
from luma.core.interface.serial import spi
from PIL import Image, ImageFont
from luma.core.virtual import terminal
from luma.core.render import canvas
from os import path
title = 'This is developed by laxz usin\' firestore'

def get_device():
    DC = 24
    RST = 25
    serial = spi(device=0, port=0, bus_speed_hz=8000000,
                 transfer_size=4096, gpio_DC=DC, gpio_RST=RST)
    return(sh1106(serial, rotate=2))


def makeFont(name, size):
    fontPath = path.abspath(path.join(path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(fontPath, size)


def main(val):
    for fontname, size in [("ProggyTiny.ttf", 16)]:
        font = makeFont(fontname, size) if fontname else None
        term = terminal(get_device(), font)
        term.println(title)
        #term.println(u'{}'.format(doc.to_dict()))
        term.println(val)
