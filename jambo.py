# Boat Control Functionality
# NRC

# import functionality
from usched import Sched # cooperative Scheduling
import compass # tiltcompensated compass
from Seatalk import seatalkthread
from barometer import barometerthread
import upower
import pyb
import time
from nmeagenerator import ERR


def run():
    OB = output_buffer()
    compassthread = compass.cthread(OB)
    pyb.delay(100)
    othread = outputthread(OB)
    objSched = Sched()
    objSched.add_thread(seatalkthread(OB))
    objSched.add_thread(compassthread)
    pyb.delay(100)
    objSched.add_thread(barometerthread(OB))
    objSched.add_thread(othread)
    objSched.run()


def outputthread(outbuf, test=False):
    if test:
        outputserial = None
    else:
        outputserial = pyb.UART(6, 115200)

    if upower.vbat() < 2.0:
        outbuf.write(ERR('Low Backup Battery').msg)
    while True:
        yield 0.1
        outbuf.print(outputserial)


class output_buffer:

    def __init__(self):
        self.buf = []
        self.log = {}
        self.load()

    def write(self, data):
        self.buf.extend(data)

    def print(self, uart):
        if len(self.buf) > 0:
            output = ''.join(self.buf)
            self.buf = []
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
        return
#        self.log['alive'] = log
#        self.save()

    def save(self):
        return
#        bkpram = upower.BkpRAM()
#        z = pickle.dumps(self.log).encode('utf8')
#        bkpram[0] = len(z)
#        bkpram.ba[4: 4+len(z)] = z # Copy into backup RAM

    def load(self):
        return
#        reason = upower.why()                           # Why have we woken?
#        if reason == 'BOOT':                            # first boot
#            self.log = log_generator()
#            self.save()
#        elif reason == 'POWERUP':
#            bkpram = upower.BkpRAM()
#            self.log = pickle.loads(bytes(bkpram.ba[4:4+bkpram[0]]).decode('utf-8')) # retrieve dictionary
#            if len(self.log) == 0:
#                self.log = log_generator()
#        currentdaydata = time.time()
#        currentdaytuple = time.localtime(currentdaydata)
        # adjust currentdaytuple to make to midnight on day of interest
#        cdt = (currentdaytuple[0], currentdaytuple[1], currentdaytuple[2], 0, 0, 0,
#               currentdaytuple[6],currentdaytuple[7])

#        date = time.mktime(cdt)

#        dt = self.log['date']
#        dist = self.log['daily'] + self.log['alive']
#        if date == dt:
#            self.log['daily'] = dist
#            self.log['alive'] = 0

        # if new day adjust all records and create history
#        elif date > dt and dist > 0:
#            hist = {'date' : dt, 'distance':dist}
#            self.log['history'].insert(0,hist)
#            self.log['history'] = self.log['history'][:-1]
#            self.log['total'] = self.log['total'] + dist

#            self.log['daily'] = 0
#            self.log['alive'] = 0
#            self.log['date'] = date


def log_generator():
    history = []
    loghistory = {'date': 0, 'distance': 0}
    for x in range(0, 30):
        history.append(loghistory)
    return {'total': 0, 'daily': 0, 'date': 0, 'alive': 0, 'history': history}

def setup():
    dt = pyb.RTC().datetime()
    if (dt[0] == 2014) and (dt[1] == 1):
        pyb.RTC().datetime((
            inputint("Year [yyyy]: ", 2014, 3000),
            inputint("Month [1..12]: ", 1, 12),
            inputint("Day of month [1..31]: ",1, 31),
            inputint("Day of week [1 = Monday]: ", 1, 7),
            inputint("Hour [0..23]: ", 0, 23),
            inputint("Minute [0..59]: ", 0, 59),
            0, 0))
        dt = pyb.RTC().datetime()
    print('RTC: {:04},{:02},{:02} {:02}:{:02}'.format(dt[0], dt[1], dt[2], dt[4], dt[5]))


def inputint(pr, mn, mx):
    x = input(pr)
    try:
        x = int(x)
    except:
        x = mn
    if (x < mn):
        x = mn
    if (x > mx):
        x = mx
    return x
