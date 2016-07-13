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
class Barometer():
    '''
    Module for the BMP180 pressure sensor.
    '''

    _bmp_addr = 119  # adress of BMP180 is hardcoded on the sensor

    # init
    def __init__(self, side_str=None):

        # choose which i2c port to use
        if side_str == 'X':
            side = 1
        elif side_str == 'Y':
            side = 2
        else:
            print('pass either X or Y, defaulting to Y')
            side = 2
        output=''
        # create i2c obect
        _bmp_addr = self._bmp_addr
        self._bmp_i2c = pyb.I2C(side, pyb.I2C.MASTER)
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
        self.oversample_setting = 3
        self.baseline = 101325.0

        # output raw
        self.UT_raw = None
        self.B5_raw = None
        self.MSB_raw = None
        self.LSB_raw = None
        self.XLSB_raw = None
        self.gauge = self.makegauge()  # Generator instance
        for _ in range(128):
            next(self.gauge)
            pyb.delay(1)

    def compvaldump(self):
        '''
        Returns a list of all compensation values
        '''
        return [self._AC1, self._AC2, self._AC3, self._AC4, self._AC5, self._AC6,
                self._B1, self._B2, self._MB, self._MC, self._MD, self.oversample_setting]

    # gauge raw
    def makegauge(self):
        '''
        Generator refreshing the raw measurments.
        '''
        delays = (5, 8, 14, 25)
        while True:
            self._bmp_i2c.mem_write(0x2E, self._bmp_addr, 0xF4)
            t_start = pyb.millis()
            while pyb.elapsed_millis(t_start) <= 5:  # 5mS delay
                yield None
            try:
                self.UT_raw = self._bmp_i2c.mem_read(2, self._bmp_addr, 0xF6)
            except:
                yield None

            self._bmp_i2c.mem_write((0x34 + (self.oversample_setting << 6)),
                                    self._bmp_addr,
                                    0xF4)

            t_pressure_ready = delays[self.oversample_setting]
            t_start = pyb.millis()
            while pyb.elapsed_millis(t_start) <= t_pressure_ready:
                yield None
            try:
                self.MSB_raw = self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF6)
                self.LSB_raw = self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF7)
                self.XLSB_raw = self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF8)
            except:
                yield None
            yield True

    def blocking_read(self):
        if next(self.gauge) is not None:  # Discard old data
            pass
        while next(self.gauge) is None:
            pass

    @property
    def oversample_sett(self):
        return self.oversample_setting

    @oversample_sett.setter
    def oversample_sett(self, value):
        if value in range(4):
            self.oversample_setting = value
        else:
            print('oversample_sett can only be 0, 1, 2 or 3, using 3 instead')
            self.oversample_setting = 3

    @property
    def temperature(self):
        '''
        Temperature in degree C.
        '''
        next(self.gauge)
        try:
            UT = unp('>h', self.UT_raw)[0]
        except:
            return 0.0
        X1 = (UT - self._AC6) * self._AC5 / 2 ** 15
        X2 = self._MC * 2 ** 11 / (X1 + self._MD)
        self.B5_raw = X1 + X2
        return (((X1 + X2) + 8) / 2 ** 4) / 10

    @property
    def pressure(self):
        '''
        Pressure in mbar.
        '''
        next(self.gauge)
        self.temperature  # Populate self.B5_raw
        try:
            MSB = unp('<h', self.MSB_raw)[0]
            LSB = unp('<h', self.LSB_raw)[0]
            XLSB = unp('<h', self.XLSB_raw)[0]
        except:
            return 0.0
        UP = ((MSB << 16) + (LSB << 8) + XLSB) >> (8 - self.oversample_setting)
        B6 = self.B5_raw - 4000
        X1 = (self._B2 * (B6 ** 2 / 2 ** 12)) / 2 ** 11
        X2 = self._AC2 * B6 / 2 ** 11
        X3 = X1 + X2
        B3 = ((int((self._AC1 * 4 + X3)) << self.oversample_setting) + 2) / 4
        X1 = self._AC3 * B6 / 2 ** 13
        X2 = (self._B1 * (B6 ** 2 / 2 ** 12)) / 2 ** 16
        X3 = ((X1 + X2) + 2) / 2 ** 2
        B4 = abs(self._AC4) * (X3 + 32768) / 2 ** 15
        B7 = (abs(UP) - B3) * (50000 >> self.oversample_setting)
        if B7 < 0x80000000:
            pressure = (B7 * 2) / B4
        else:
            pressure = (B7 / B4) * 2
        X1 = (pressure / 2 ** 8) ** 2
        X1 = (X1 * 3038) / 2 ** 16
        X2 = (-7357 * pressure) / 2 ** 16
        return pressure + (X1 + X2 + 3791) / 2 ** 4

    @property
    def altitude(self):
        '''
        Altitude in m.
        '''
        try:
            p = -7990.0 * math.log(self.pressure / self.baseline)
        except:
            p = 0.0
        return p

    def update(self):
        self.output = MDA(self.pressure // 100).msg


    # standard function to write data to UART


def barometerthread(out_buf):
    barometer = Barometer(side_str='X')
    wf = Timeout(6)                        # Instantiate a Poller with 60 second timeout.
    while True:
        barometer.update()
        out_buf.write(barometer.output)
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
