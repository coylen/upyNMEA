# provides the control of the I2C selector control and provides data for the decoding functions
# NRC

from usched import Sched, Timeout, wait
from nasadepth import NASADepth
from nasawind import NASAWind
import pyb


def NASADepthThread(output_buffer):
    nd = NASADepth(side_str='Y', pin=pyb.Pin.board.X8, pin_value=1)
    while True:
        nd.update(output_buffer)
        yield 1


def NASAWindThread(output_buffer):
    nw = NASAWind(side_str='Y', pin=pyb.Pin.board.X8, pin_value=0)
    while True:
        nw.update(output_buffer)
        yield 1
