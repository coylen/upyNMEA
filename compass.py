# Simple test program for sensor fusion on Pyboard
# Author Peter Hinch
# V0.7 25th June 2015 Adapted for new MPU9x50 interface

import pyb
from mpu9250 import MPU9250
from fusion import Fusion
from usched import Sched, Poller, wait
from nmeagenerator import HDG

i2c_object = None

def stop(fTim, objSch):                                     # Stop the scheduler after fTim seconds
    yield from wait(fTim)
    objSch.stop()


class TiltCompensatedCompass:

    def __init__(self, imu):
        self.imu = imu
        self.fuse = Fusion()
        self.update()
        self.hrp = [self.fuse.heading, self.fuse.roll, self.fuse.pitch]

    def poll(self, dummy):
        self.update()
        if self.hrp[0] != self.fuse.heading:
            self.hrp = [self.fuse.heading, self.fuse.roll, self.fuse.pitch]
            return 1
        return None

    def update(self):
        accel = self.imu.accel.xyz
        gyro = self.imu.gyro.xyz
        mag = self.imu.mag.xyz
        self.fuse.update(accel, gyro, mag)

    @property
    def heading(self):
        return self.hrp[0]

    @property
    def roll(self):
        return self.hrp[1]

    @property
    def pitch(self):
        return self.hrp[2]

    @property
    def output(self):
        return HDG(self.hrp[0])

def cthread(link=None):
    imu = MPU9250('X')
    global i2c_object
    i2c_object = imu._mpu_i2c
    yield from wait(0.03)                                   # Allow accelerometer to settle
    compass = TiltCompensatedCompass(imu)
    wf = Poller(compass.poll, (4,), 1)                        # Instantiate a Poller with 1 second timeout.
    while True:
        reason = (yield wf())
        if link is None:
            print("Value heading:{:3d} roll:{:3d} pitch:{:3d}".format(compass.heading, compass.roll, compass.pitch))
        else:
            #TODO create output to serial port
            print(compass.output)


# USER TEST PROGRAM

def test(duration=0):
    if duration:
        print("Output accelerometer values for {:3d} seconds".format(duration))
    else:
        print("Output accelerometer values")
    objSched = Sched()
    objSched.add_thread(cthread())
    if duration:
        objSched.add_thread(stop(duration, objSched))           # Run for a period then stop
    objSched.run()

test(30)

# imu = MPU9150('X')
#
# fuse = Fusion()
#
# # Choose test to run
# Calibrate = True
# Timing = False
#
# def getmag():                               # Return (x, y, z) tuple (blocking read)
#     return imu.mag.xyz
#
# if Calibrate:
#     print("Calibrating. Press switch when done.")
#     sw = pyb.Switch()
#     fuse.calibrate(getmag, sw, lambda : pyb.delay(100))
#     print(fuse.magbias)
#
# if Timing:
#     mag = imu.mag.xyz # Don't include blocking read in time
#     accel = imu.accel.xyz # or i2c
#     gyro = imu.gyro.xyz
#     start = pyb.micros()
#     fuse.update(accel, gyro, mag) # 1.65mS on Pyboard
#     t = pyb.elapsed_micros(start)
#     print("Update time (uS):", t)
#
# count = 0
# while True:
#     fuse.update(imu.accel.xyz, imu.gyro.xyz, imu.mag.xyz) # Note blocking mag read
#     if count % 50 == 0:
#         print("Heading, Pitch, Roll: {:7.3f} {:7.3f} {:7.3f}".format(fuse.heading, fuse.pitch, fuse.roll))
#     pyb.delay(20)
#     count += 1
