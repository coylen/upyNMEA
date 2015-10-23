# provides the control of the I2C selector control and provides data for the decoding functions
# NRC

from usched import Sched, Timeout, wait
from nasadepth import NASADepth
from nasawind import NASAWind


def stop(fTim, objSch):                                     # Stop the scheduler after fTim seconds
    yield from wait(fTim)
    objSch.stop()

def NASADepthThread():  # I2C, control_pin, cp_value):
    nd = NASADepth('X',1,1)
    wf = Timeout(0.5)
    while True:
        # control_pin.value(cp_value)  # set control pin to defined value to allow I2C read
        nd.update()
        yield wf()


def NASAWindThread():  # I2C, control_pin, cp_value):
    nw = NASAWind('X',1,1)
    wf = Timeout(0.5)
    while True:
        # control_pin.value(cp_value)  # set control pin to defined value to allow I2C read
        nw.update()
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