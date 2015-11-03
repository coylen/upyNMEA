#import pyb


# template class for NASA Instruments
class NASAException(OSError):
    # Exception for NASA devices
    pass


class NASA:

    _I2Cerror = "I2C failure when communicating with NASA INSTRUMENTS"

    def __init__(self, i2c_object=None, side_str=None, pin=None, pin_value=None, link=None):

        if side_str == 'X':
            side = 1
        elif side_str == 'Y':
            side = 2
        else:
            side = 2

        if i2c_object is None:
            print('init')
            #self.I2C = pyb.I2C(side, pyb.I2C.SLAVE, addr=0x3e)
        else:
            print('obj')
            self.I2C = i2c_object

        self.pin = pin
        self.pin_value = pin_value
        self.packet_size = 0
        self.data = []
        self.output = ""
        self.link = link

    def update(self):
        self.receive()
        self.decode()
        self.send()

    def receive(self):
        # TODO: pin control to be implimented for multiple units on chip
        try:
            self.data = self.I2C.recv(self.packet_size)
        except OSError:
            raise NASAException(self._I2Cerror)

    # template for process function of specific class
    def decode(self):
        pass

    # standard function to write data to UART
    def send(self):
        # TODO: Add UART OUTPUT
        if self.link is None:
            print(self.output)
            self.output = ''
        else:
            self.link.write(self.output)

    @staticmethod
    def mask(data, msk):
        if len(data) == len(msk):
            masked_data = bytearray()
            for d, m in data, msk:
                masked_data.append(d & m)

            return masked_data

    @staticmethod
    def lowestSet(int_type):
        low = int_type & -int_type
        lowbit = -1
        while low:
            low >>= 1
            lowbit += 1
        return lowbit

    @staticmethod
    def bitCount(int_type):
        count = 0
        while int_type:
            int_type &= int_type - 1
            count += 1
        return count

    @staticmethod
    def digitdecode(data, digitmask, digitcontrol):
        digitdata = NASA.mask(data, digitmask)
        for x in range(0, 10):
            if digitdata == digitcontrol[x]:
                return x
        return -1
