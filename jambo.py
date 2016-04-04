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
    OB = output_buffer()
    compassthread = compass.cthread(OB) # temp dummy link
    mpu_i2c = compass.i2c_object
    pyb.delay(100)
    othread = outputthread(OB, test=True)
    objSched=Sched()
    objSched.add_thread(seatalkthread(OB))
#    objSched.add_thread(compassthread)
#    objSched.add_thread(NASAWindThread())
#    objSched.add_thread(NASADepthThread())
    mpu_i2c = compass.i2c_object
    pyb.delay(100)
#    objSched.add_thread(barometerthread(i2c_object=mpu_i2c))
    objSched.add_thread(othread)
    objSched.run()

def outputthread(outbuf, test = False):
    if test:
        outputserial= None
    else:
        outputserial=pyb.UART(6, 115200)

    while True:
        yield 1
        outbuf.print(outputserial)
#        outbuf.clear()
        # if test:
        #
        #     print(''.join(outbuf))
        # else:
        #     outputserial.write(''.join(outbuf))
        # outbuf=[]

class output_buffer:

    def __init__(self):
        self.buf = []

    def write(self, data):
        self.buf.extend(data)

    def print(self, uart):
        if len(self.buf)>0:
            output = ''.join(self.buf)
            self.buf=[]
            if uart == None:
                print(output)
            else:
                uart.write(output)



