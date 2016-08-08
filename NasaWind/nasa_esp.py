#import pyb
from machine import Pin
from slave import I2C_SLAVE
from nmeagenerator import ERR

# template class for NASA Instruments
class NASAException(OSError):
    # Exception for NASA devices
    pass


class NASA:

    _I2Cerror = "I2C failure when communicating with NASA INSTRUMENTS"

    def __init__(self, scl=Pin(5), sda=Pin(4)):

        self.I2C = I2C_SLAVE(scl,sda)
        self.packet_size = 0
        self.data = []
        self.output = []

    def update(self):
        try:
            self.receive()
            self.decode()
        except NASAException:
            self.output.append(ERR(self._I2Cerror).msg)
            #self.I2C.init(pyb.I2C.SLAVE, addr=0x3e) #TODO hack?


    def receive(self):
        try:
            #self.pin.value(self.pin_value)
            self.data = self.I2C.read(self.packet_size)
        except OSError:
            raise NASAException(self._I2Cerror)

    # template for process function of specific class
    def decode(self):
        pass

    @staticmethod
    def mask(data, msk):
        if len(data) == len(msk):
            masked_data = bytearray()
            for x in range(0,len(data)):
                masked_data.append(data[x] & msk[x])

            return masked_data

    @staticmethod
    def digitdecode(data, digitmask, digitcontrol):
        digitdata = NASA.mask(data, digitmask)
        for x in range(0, 10):
            if digitdata == digitcontrol[x]:
                return x
        return -1

    @staticmethod
    def validbitandposition(barray):
        print(barray)
        nibble_lookup = (0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4)
        position_lookup = (0, 1, 2, -1, 3, -1, -1, -1, 4, -1, -1, -1, -1, -1, -1, -1)
        count = 0
        position = 0
        bl = len(barray)
        for x in range(0, bl):
            bte = barray[x]
            count += nibble_lookup[bte & 0x0F] + nibble_lookup[bte >> 4]
            pl = position_lookup[bte & 0x0F]
            if pl > 0:
                position = pl + (bl-x-1)*8
            pl = position_lookup[bte >> 4]
            if pl > 0:
                position = pl + (bl-x-1)*8 + 4
        if count != 1:
            raise ValueError()
        return position

