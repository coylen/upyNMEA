# Boat Control Functionality
# NRC

# import functionality
from usched import Sched # cooperative Scheduling
import compass # tiltcompensated compass
from nasacontrol import NASADepthThread, NASAWindThread
from Seatalk import seatalkthread
from barometer import barometerthread
import pyb
import time


def run():
    # setup uart object to pass
  #  output = pyb.UART(1, 4800)
    # generate objects
    OB = output_buffer()
    compassthread = compass.cthread(OB)
    mpu_i2c = compass.i2c_object
    pyb.delay(100)
    othread = outputthread(OB, test=True)
    objSched=Sched()
    objSched.add_thread(seatalkthread(OB))
#    objSched.add_thread(compassthread)
#    objSched.add_thread(NASAWindThread(OB))
#    objSched.add_thread(NASADepthThread(OB))
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
        self.log = self.load()

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

    # provide interface to backup ram data]
    # load and save commands, need to decide upon dictionary format

    # dictionary format
            # total - total trip log since reset maybe forever, maybe annually
            # daily - log for this calender day (switched on day)
            # alive - log on current instrument
            # date - valid date for log setting
            # history - date and daily log mileage for the last 30 sailing days
                # date - log date
                # distance - log distance for day
    def logupdate(self, log):
        self.log['alive'] = log
        self.save()

    def save(self):
        #TODO: write data to backup registers
        pass

    def load(self):
        #TODO: recover data from backup registers


        currentdaydata = time.time()
        currentdaytuple = time.localtime(currentdaydata)
        # adjust currentdaytuple to make to midnight on day of interest
        date = time.mktime(currentdaytuple)

        dt = self.log['date']
        dist = self.log['daily'] + self.log['alive']
        if date == dt:
            self.log['daily'] = dist
            self.log['alive'] = 0

        # if new day adjust all records and create history
        elif date > dt:
            hist = {'date':dt, 'distance':dist}
            self.log['history'].insert(0,hist)
            self.log['history'] = self.log['history'][:-1]
            self.log['total'] = self.log['total'] + dist
        # if date current create new alive


def log_generator():
    history = []
    loghistory = {'date':0, 'distance':0}
    for x in range(0,30):
        history.append(loghistory)
    return {'total': 0, 'daily': 0, 'date':0, 'alive':0, 'history':history}

