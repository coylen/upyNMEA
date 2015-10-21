import pyb

# template class for NASA Instruments
class NASA:

    def __init__(self, i2c, pin, pin_value):
        self.I2C = pyb.I2C(i2c, pyb.I2C.SLAVE, addr=0x3e)
        self.pin = pin
        self.pin_value = pin_value
        self.packet_size = 0
        self.data = []
        self.output=""

    def update(self):
        self.recieve()
        self.decode()
        self.send()

    def recieve(self):
        # TODO: pin control to be implimented for multiple units on chip
        try:
            self.data = self.I2C.recv(self.packet_size)
        except:
            pass

    # template for process function of specific class
    def decode(self):
        pass

    # standard function to write data to UART
    def send(self):
        pass

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

