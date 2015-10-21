# Boat Control Functionality
# NRC

#import functionality
from pyb import UART
from usched import Sched, Poller, wait # cooperative Scheduling
from compass import compassthread # tiltcompensated compass
from nasacontrol import NASADepthThread, NASAWindThread
from Seatalk import seatalkthread


def run():
    #setup uart object to pass
    objSched=Sched()
    objSched.add_thread(seatalkthread())
    objSched.add_thread(compassthread())
    objSched.add_thread(NASAWindThread())
    objSched.add_thread(NASADepthThread())
    objSched.run()




