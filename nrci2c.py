# bitbang i2c slave test

# scheme
# SDAint - rise and fall
# SCLint - rise only

from machine import Pin, I2C


bitnum = 0
bit = 0
byte = 0
bytenum = 0
data = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

start = True #False
finished = False
SDA = Pin(4,Pin.IN)
SCL = Pin(5,Pin.IN)
disabled = False


# handler for falling SDA - if combined with a high SCL indicates start condition
# handler for rising SDA - if combined with a high SCL indicates stop condition
def SDAcall(t):
    global start, finished, disabled, SDA, SCL
    if not disabled:
        if SCL.value() == 1:
            start = False
            finished = True
            print('end')



# handler for rising SCL - indicates data ready to read
def SCLcall(t):
    global start, bit, bitnum, byte, bytenum, data, finished, SDA, SCL
    # check we have start bit and therfore valid
   # if start:
    bitnum += 1
    byte = (byte << 1) | SDA()
    if bitnum==8:
        data[bytenum] = byte
        bytenum += 1
        bitnum = 0
        byte = 0
   #      print('byte')
   #      if bytenum == 20:
   #          finished = True
   #          start =False


def run():
    global start, bit, bitnum, byte, bytenum, data, finished, disabled, SDA, SCL
    # main loop
#    SDA.irq(Pin.IRQ_FALLING, SDAcall)
    SCL.irq(Pin.IRQ_RISING, SCLcall)

    while True:
        if finished:
            disabled = True
            print("{} {}".format(bytenum, bitnum))
            print(data)
            data = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            bitnum = 0
            bit = 0
            byte = 0
            bytenum = 0
            finished = False
            disabled = False

##seperate paste
from machine import Pin
from slave import I2C_SLAVE
i2c=I2C_SLAVE(Pin(5),Pin(4))
i2c.read(5)

#old
from machine import Pin, I2C
i2c=I2C(scl=Pin(5),sda=Pin(4), freq=125000)
i2c.readfrom(0x3e, 1)


#pyboard
import pyb
a=pyb.I2C(1,pyb.I2C.MASTER, baudrate=100000)
a.scan()
