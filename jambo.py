# Boat Control Functionality
# NRC

# import functionality
from usched import Sched # cooperative Scheduling
import compass # tiltcompensated compass
from nasacontrol import NASADepthThread, NASAWindThread
from Seatalk import seatalkthread
from barometer import barometerthread
import pyb

def run():
    # setup uart object to pass
  #  output = pyb.UART(1, 4800)
    # generate objects
    compassthread = compass.cthread()#link=output)
    mpu_i2c = compass.i2c_object
    pyb.delay(100)


    objSched=Sched()
#    objSched.add_thread(seatalkthread())
    objSched.add_thread(compassthread)
#    objSched.add_thread(NASAWindThread())
#    objSched.add_thread(NASADepthThread())
    mpu_i2c = compass.i2c_object
    pyb.delay(100)
    objSched.add_thread(barometerthread(i2c_object=mpu_i2c))
    objSched.run()




