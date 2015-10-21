# provides the control of the I2C selector control and provides data for the decoding functions
# NRC

import pyb
from usched import Sched, Timeout, wait
import nasadepth
import nasawind


def stop(fTim, objSch):                                     # Stop the scheduler after fTim seconds
    yield from wait(fTim)
    objSch.stop()

# define initialisation constants
NasaI2C = pyb.I2C(1, pyb.I2C.SLAVE, addr=0x3E)
# need to define control pin


def NASADepthThread():  # I2C, control_pin, cp_value):
    wf = Timeout(0.5)
    while True:
        # control_pin.value(cp_value)  # set control pin to defined value to allow I2C read
        data = nasadepth.receive(NasaI2C)
        depth = nasadepth.decode(data)
        if depth is not None:
            print(depth)
        yield wf()


def NASAWindThread():  # I2C, control_pin, cp_value):
    wf = Timeout(0.5)
    while True:
        # control_pin.value(cp_value)  # set control pin to defined value to allow I2C read
        data = nasawind.receive(NasaI2C)
        direction, windspeed = nasawind.decode(data)
        print("dir: {0} speed: {1}".format(direction, windspeed))
        yield wf()


# USER TEST PROGRAM
def test(duration=0):
    if duration:
        print("Output Nasa Depth values for {:3d} seconds".format(duration))
    else:
        print("Output Nasa depth values")
    objSched = Sched()
    objSched.add_thread(NASADepthThread())
    if duration:
        objSched.add_thread(stop(duration, objSched))           # Run for a period then stop
    objSched.run()

test(30)

class