#import pyb
#from usched import Sched, Poller, wait,Roundrobin
from nmeagenerator import VHW, VLW, ERR


class Seatalk:
    def __init__(self, stream, offset):
        # values
        self.speedthroughwater = 0
        self.averagespeedthroughwater = 0
        self.trip = 0
        self.totaltrip = 0
        self.data = []
        # self.buff=[]
        self.command = 0
        self.length = 0
        self.offset = offset
        # flags
        # self.speedthroughwater_changed = False
        # self.averagespeedthroughwater_changed = False
        self.trip_changed = False
        # self.totaltrip_changed = False
        self.status = Status.Empty

        self.output = []
        # sentences understood
        self.Decode = {32: self.Speed_through_water_20,
                       33: self.Trip_milage_21,
                       34: self.Total_milage_22,
                       37: self.Total_and_trip_25,
                       38: self.Speed_through_water_26}
        # setup uart
        self.stream = stream

    def Poll(self, dummy):
        if self.stream.any():
            uart_data = self.stream.read(2)
            if self.process(uart_data):
                return 1
        return None

    def process(self, data):
        # loop while data available
        x = 0
        while len(data) > x+1:
            newdata = data[x]
            parity = data[x+1]
            x += 2

            # if command bit set, set status to command
            if self.paritycheck(parity):
                self.command = newdata
                self.data = []
                self.status = Status.Command

            # if on command status check for length
            elif self.status == Status.Command and self.paritycheck(parity) is False:
                self.data.append(newdata)
                self.length = (newdata & 0x0F) + 1
                self.status = Status.Length

            # if on length status collect data to match length
            elif self.status == Status.Length and self.paritycheck(parity) is False:
                self.data.append(newdata)
                self.length -= 1
                # if length is achieved mark as complete
                if self.length == 0:
                    self.status = Status.Complete

            # if status is complete
            if self.status == Status.Complete:
                out = ''
                try:
                    out = self.Decode[self.command](self.data)
                except:
                    out = ERR("{:2x} SEATALK SENTENCE NOT RECOGNISED".format(self.command)).msg
                finally:
                    self.output.append(out)
                    self.status = Status.Empty
                    return True
        return False

    @staticmethod
    def paritycheck(byte):
        if byte == 1:
            return True
        else:
            return False

# Decode sections
# TODO: deos int.from_bytes work?
#  20  01  XX  XX  Speed through water: XXXX/10 Knots
#                  Corresponding NMEA sentence: VHW
    def Speed_through_water_20(self, data):
        if len(data) == 3:
            self.speedthroughwater = (data[1]+data[2]*256) / 10.0
            # self.speedthroughwater_changed = True
            return VHW(self.speedthroughwater).msg
        return ERR('ST 20 incorrect length: {}'.format(len(data))).msg


#  21  02  XX  XX  0X  Trip Mileage: XXXXX/100 nautical miles
#                  Flag Z&4: Sensor defective or not connected (Z=4)
#                  Corresponding NMEA sentence: MTW
    def Trip_milage_21(self, data):
        if len(data) == 4:
            self.trip = (data[0]+data[1]*256+(data[2]&0x0F)*4096) / 100.0
            self.trip_changed = True
            return VLW(self.trip+self.offset).msg
        return ERR('ST 21 incorrect length: {}'.format(len(data))).msg

#  22  02  XX  XX  00  Total Mileage: XXXX/10 nautical miles
    def Total_milage_22(self, data):
        if len(data) == 4:
            self.totaltrip = (data[1]+data[2]*256) / 10.0
            #  self.totaltrip_changed = True
            return "TOTAL TRIP {0}".format(self.totaltrip)  # TODO: Create NMEA for this of remove
        return ERR('ST 22 incorrect length: {}'.format(len(data))).msg

#  25  Z4  XX  YY  UU  VV AW  Total & Trip Log
#                      total= (XX+YY*256+Z* 4096)/ 10 [max=104857.5] nautical miles
#                      trip = (UU+VV*256+W*65536)/100 [max=10485.75] nautical miles
    def Total_and_trip_25(self, data):
        if len(data) == 6:
            self.totaltrip = (data[1] + data[2]*256 + (data[0] >> 4)*4096) / 10
            self.trip = (data[3] + data[4]*256 + (data[5] & 0x0F)*4096) / 100
            self.trip_changed = True
            # self.totaltrip_changed = True
            return VLW(self.trip + self.offset).msg
# TODO:            self.output += "TOTAL TRIP {0}".format(self.totaltrip) # TODO: Create NMEA for this of remove
        return ERR('ST 25 incorrect length: {}'.format(len(data))).msg

#  26  04  XX  XX  YY  YY DE  Speed through water:
#                      XXXX/100 Knots, sensor 1, current speed, valid if D&4=4
#                      YYYY/100 Knots, average speed (trip/time) if D&8=0
#                               or data from sensor 2 if D&8=8
#                      E&1=1: Average speed calulation stopped
#                      E&2=2: Display value in MPH
#                      Corresponding NMEA sentence: VHW
    def Speed_through_water_26(self, data):
        if len(data) == 6:
            self.speedthroughwater = (data[0]+data[1]*256) / 100
            self.averagespeedthroughwater = (data[2]+data[3]*256) / 100
            # self.speedthroughwater_changed = True
            # self.averagespeedthroughwater_changed = True
            return VHW(self.speedthroughwater).msg
        return ERR('ST 26 incorrect length: {}'.format(len(data))).msg

    def update(self,output_buffer):
        output_buffer.write(self.output)
        self.output = []
        if self.trip_changed:
            output_buffer.logupdate(self.trip)
            self.trip_changed = False


class Status:
    Empty = 0
    Command = 1
    Length = 2
    Complete = 3


def seatalkthread(out_buff):
    stream = pyb.UART(4, 4800, bits=9)
    yield 0.5
    st = Seatalk(stream, out_buff.log['daily'])
    wf = Poller(st.Poll, (4,), 5)
    while True:
        reason = (yield wf())
        if reason[1]:
            st.update(out_buff)
            #out_buff.write(st.output)
            #st.output = []
        if reason[2]:
            out_buff.write(ERR('ST DATA TIMEOUT').msg)


# def stop(fTim, objSch):
#     yield from wait(fTim)
#     objSch.stop()
#
#
# def testprocess(duration=0):
#     stream = pyb.UART(1, 4800, bits=9)
#     st=Seatalk(stream)
#     while True:
#         st.Poll()
#
# def test(duration=0):
#     if duration:
#         print("capture seatalk data for {:3d} seconds".format(duration))
#     else:
#         print("Capture seatalk data")
#     objSched = Sched()
#     objSched.add_thread(seatalkthread())
#     if duration:
#         objSched.add_thread(stop(duration, objSched))
#     objSched.run()
# #
# # test(30)
#
# def basic():
#      stream = pyb.UART(1, 4800, bits=9)
#      while True:
#          while stream.any():
#              dat=stream.read(2)
#              print("{0}  {1}".format(dat[0],dat[1]))
#              if dat[1]==1 and dat[0]<27:
#                  print('EUREKA')
#
# print('seatalk test suite')
# print(' basic() to show data recieving')
# print(' testprocess() to check process')
# print('test to test scheduling')
#
# class log:
#     def __init__(self, stream, link=None):
#         pass
#
#     def load(self):
#         pass
#
#     def save(self):
#         pass
#
#     def update(self):
#         pass
#

a=Seatalk(0,0)
a.command= 32
a.data=[33,0,255]
a.Decode[a.command](a.data)