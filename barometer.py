# Simple test program for sensor fusion on Pyboard
# Author Peter Hinch
# V0.7 25th June 2015 Adapted for new MPU9x50 interface

import pyb
from bmp180 import BMP180
from usched import Sched, Timeout, wait
from nmeagenerator import MDA
from struct import unpack as unp


def stop(fTim, objSch):                                     # Stop the scheduler after fTim seconds
    yield from wait(fTim)
    objSch.stop()


# Subclassed Micropython_BMP and copied Init to avoid need to call super
# this allows initialisation of device using existing I2C object
class Barometer(BMP180):

    def __init__(self, i2c_object=None, side_str=None, link=None):

        # choose which i2c port to use
        if i2c_object is None:
            if side_str == 'X':
                side = 1
            elif side_str == 'Y':
                side = 2
            else:
                print('pass either X or Y, defaulting to Y')
                side = 2

            # create i2c obect

            self._bmp_i2c = pyb.I2C(side, pyb.I2C.MASTER)
        else:
            self._bmp_i2c = i2c_object

        self.link=link
        _bmp_addr = self._bmp_addr
        self.chip_id = self._bmp_i2c.mem_read(2, _bmp_addr, 0xD0)
        # read calibration data from EEPROM
        self._AC1 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xAA))[0]
        self._AC2 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xAC))[0]
        self._AC3 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xAE))[0]
        self._AC4 = unp('>H', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB0))[0]
        self._AC5 = unp('>H', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB2))[0]
        self._AC6 = unp('>H', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB4))[0]
        self._B1 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB6))[0]
        self._B2 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB8))[0]
        self._MB = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xBA))[0]
        self._MC = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xBC))[0]
        self._MD = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xBE))[0]

        # settings to be adjusted by user
        self.oversample_sett = 3
        self.baseline = 101325.0

        # private attributes not to be used by user
        self._t_temperature_ready = None
        self._UT = None
        self._t_pressure_ready = None
        self._B5 = None

        # output raw
        self.UT_raw = None
        self.B5_raw = None
        self.MSB_raw = None
        self.LSB_raw = None
        self.XLSB_raw = None

        for _ in range(128):
            next(self.gauge())
            pyb.delay(1)

        self.output = ''

    def update(self):
        self.output = MDA(self.pressure // 100)
        self.send()

    # standard function to write data to UART
    def send(self):
        # TODO: Add UART OUTPUT
        if self.link is None:
            print(self.output.msg)
            self.output = ''
        else:
            self.link.write(self.output)

def barometerthread(i2c_object=None, side_str=None, link=None):
    if i2c_object is None:
        side_str='X'
    barometer = Barometer(i2c_object,side_str, link)
    wf = Timeout(6)                        # Instantiate a Poller with 60 second timeout.
    while True:
        barometer.update()
        yield wf()


# USER TEST PROGRAM

def test(duration=0):
    if duration:
        print("Output accelerometer values for {:3d} seconds".format(duration))
    else:
        print("Output accelerometer values")
    objSched = Sched()
    objSched.add_thread(barometerthread())
    if duration:
        objSched.add_thread(stop(duration, objSched))           # Run for a period then stop
    objSched.run()

#test(30)
