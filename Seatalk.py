import pyb
from usched import Sched, Poller, wait,Roundrobin

class Seatalk:
    def __init__(self, stream):
        #values
        self.speedthroughwater=0
        self.averagespeedthroughwater=0
        self.trip=0
        self.totaltrip=0
        self.data=[]
        #self.buff=[]
        self.command=0
        self.data=[]
        self.length=0
        #flags
        self.speedthroughwater_changed=False
        self.averagespeedthroughwater_changed=False
        self.trip_changed=False
        self.totaltrip_changed=False
        self.status=0

        #sentences understood
        self.Decode={ 32:self.Speed_through_water_20,
                        33:self.Trip_milage_21,
                        34:self.Total_milage_22,
                        37:self.Total_and_trip_25,
                        38:self.Speed_through_water_26}
        #setup uart
        self.stream=stream

    def Poll(self):
        uart_data=self.stream.readall()
        Process(uart_data)
        if self.speedthroughwater_changed:
            return 1
        return none

    def Process(self,data):
       #loop while data available
        while len(data)>1:
            newdata=data.pop(0)
            parity=data.pop(0)

            #if command bit set, set status to command
            if self.paritycheck(parity)==True:
                self.command=newdata
                self.status=Status.Command
            #if on command status check for length
            elif self.status==Status.Command & self.paritycheck(parity)==False:
                self.data=newdata
                self.length=newdata&0x0F+2
                self.status=Status.Length
            #if on length status collect data to match length
            elif self.status==Status.Length & self.paritycheck(parity)==False:
                self.data.append(newdata)
                self.length-=1
            #if length is achieved mark as complete
                if self.length==0:
                    self.status=Status.Complete
            #if status is complete
            if self.status==Status.Complete:
                self.Decode[self.command](self.data)
                self.status=Status.Empty
        return

    def paritycheck(self,byte):
        if byte[1]==1:
            return True
        else:
            return False
#    def Read

    def isvalid(self,commandbytes):
        #check parity bit is correct

        #check command is known

        return True


#Decode sections

#  20  01  XX  XX  Speed through water: XXXX/10 Knots
#                  Corresponding NMEA sentence: VHW
    def Speed_through_water_20(self,data):
        if len(data)==3:
            self.speedthroughwater=(int.from_bytes(data[:-2], byteorder='little'))/10.0
            self.speedthroughwater_changed=True
        return


#  21  02  XX  XX  0X  Trip Mileage: XXXXX/100 nautical miles
#                  Flag Z&4: Sensor defective or not connected (Z=4)
#                  Corresponding NMEA sentence: MTW
    def Trip_milage_21(self,data):
        if len(data)==4:
            self.trip=(int.from_bytes(data[:-3], byteorder='little'))/100.0
            self.trip_changed=True
        return

#  22  02  XX  XX  00  Total Mileage: XXXX/10 nautical miles
    def Total_milage_22(self,data):
        if len(data)==4:
            self.totaltrip=(int.from_bytes(data[:-3], byteorder='little'))/10.0
            self.totaltrip_changed=True
        return

#  25  Z4  XX  YY  UU  VV AW  Total & Trip Log
#                      total= (XX+YY*256+Z* 4096)/ 10 [max=104857.5] nautical miles
#                      trip = (UU+VV*256+W*65536)/100 [max=10485.75] nautical miles
    def Total_and_trip_25(self,data):
        if len(data)==6:
            self.totaltrip=(data[1]+data[2]*256+(data[0]>>4)*4096)/10
            self.trip=(data[3]+data[4]*256+(data[5]&0x0F)*4096)/100
            self.trip_changed=True
            self.totaltrip_changed=True
        return

#  26  04  XX  XX  YY  YY DE  Speed through water:
#                      XXXX/100 Knots, sensor 1, current speed, valid if D&4=4
#                      YYYY/100 Knots, average speed (trip/time) if D&8=0
#                               or data from sensor 2 if D&8=8
#                      E&1=1: Average speed calulation stopped
#                      E&2=2: Display value in MPH
#                      Corresponding NMEA sentence: VHW
    def Speed_through_water_26(self,data):
        if len(data)==6:
            self.speedthroughwater=(int.from_bytes(data[1:3], byteorder='little'))/100
            self.averagespeedthroughwater=(int.from_bytes(data[3:5], byteorder='little'))/100
            self.speedthroughwater_changed=True
            self.averagespeedthroughwater_changed=True
        return

class Status:
    Empty=0
    Command=1
    Length=2
    Complete=3

def seatalkthread():
    stream=pyb.UART(1,4800,bits=9)
    yield from wait(0.5)
    st=Seatalk(stream)
    wf=Poller(st.Poll,(4,),1)
    while True:
        reason=(yield wf())
        if reason[1]:
            print("speed changed event")
            st.speedthroughwater_changed=False
        if reason[2]:
            print("time out event")



def stop(fTim,objSch):
    yield from wait(fTim)
    objSch.stop()

def test(duration=0):
    if duration:
        print("capture seatalk data for {:3d} seconds".format(duration))
    else:
        print("Capture seatalk data")
    objSched=Sched()
    objSched.add_thread(seatalkthread())
    if duration:
        objSched.add_thread(stop(duration,objSched))
    objSched.run()

test(30)
