from nasa_esp import NASA
from nmeagenerator import VWR, ERR
from machine import Pin

class NASAWind(NASA):

    _I2Cerror = "I2C failure when communicating with NASA WIND INSTRUMENT"

    def __init__(self, scl=Pin(5), sda=Pin(4)):
        super().__init__(scl, sda)
        self.packet_size = 18 # increased in size for address


    COMMAND = bytes(b'\x7C\xC8\x80\xE0\xF8\x70')
    DECPOINT_MASK = bytes(b'\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00')
    DIGIT1_MASK = bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x70\x00')
    DIGIT2_MASK = bytes(b'\x00\x00\x00\xF0\x00\x00\x00\x00\x07\x00\x00\x00')

    DIGIT1 = [bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x30\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0D\x00\x00\x60\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x40\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x50\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0B\x00\x00\x50\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0B\x00\x00\x70\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x70\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x50\x00')]

    DIGIT2 = [bytes(b'\x00\x00\x00\xF0\x00\x00\x00\x00\x03\x00\x00\x00'),
              bytes(b'\x00\x00\x00\x60\x00\x00\x00\x00\x00\x00\x00\x00'),
              bytes(b'\x00\x00\x00\xD0\x00\x00\x00\x00\x06\x00\x00\x00'),
              bytes(b'\x00\x00\x00\xF0\x00\x00\x00\x00\x04\x00\x00\x00'),
              bytes(b'\x00\x00\x00\x60\x00\x00\x00\x00\x05\x00\x00\x00'),
              bytes(b'\x00\x00\x00\xB0\x00\x00\x00\x00\x05\x00\x00\x00'),
              bytes(b'\x00\x00\x00\xB0\x00\x00\x00\x00\x07\x00\x00\x00'),
              bytes(b'\x00\x00\x00\x70\x00\x00\x00\x00\x00\x00\x00\x00'),
              bytes(b'\x00\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00'),
              bytes(b'\x00\x00\x00\xF0\x00\x00\x00\x00\x05\x00\x00\x00')]

    DIRECTION_MASK = bytes(b'\x0F\xFF\x0F\x0F\xFF\xF0\x00\xF0\xF0\xFF\x0F\xFF')
    DIRECTION = {0: 246, 1: 258, 2: 252, 3: 264, 4: 240, 5: 228, 6: 234, 7: 222,
                 8: 288, 9: 276, 10: 282, 11: 270,
                 16: 294, 17: 306, 18: 300, 19: 312, 20: 336, 21: 324, 22: 330, 23: 318,
                 28: 198, 29: 210, 30: 204, 31: 216,
                 36: 192, 37: 180, 38: 186, 39: 171,
                 52: 342, 53: 354, 54: 348, 55: 0,
                 56: 78, 57: 90, 58: 84, 59: 96, 60: 72, 61: 60, 62: 66, 63: 54,
                 64: 30, 65: 42, 66: 36, 67: 48,
                 72: 24, 73: 12, 74: 18, 75: 6,
                 80: 102, 81: 114, 82: 108, 83: 120, 84: 144, 85: 132, 86: 138, 87: 126,
                 88: 150, 89: 162, 90: 156, 91: 168}

    def decode(self):
        # set data with error values
        direction = -1
        windspeed = -1

        #TODO HACK INCLUDED ADDRESS AS COMMAND BITS
        # Changed 5 to 6
        # check first five bytes of data for validity
        if self.data[:6] == self.COMMAND:
            self.data = self.data[6:]  # strip this preamble before further processing

            try:
                directiondata = self.mask(self.data, self.DIRECTION_MASK)
                direction = self.DIRECTION[self.validbitandposition(directiondata)]
                if direction >= 180:
                    wind_angle = abs(direction - 360)
                    left_right = 'L'
                elif direction >= 0:
                    wind_angle = direction
                    left_right = 'R'
            except:
                self.output.append(ERR('NASA WIND DIRECTION ERROR').msg)

            digit1 = -1
            digit2 = -1
            digit1 = self.digitdecode(self.data, self.DIGIT1_MASK, self.DIGIT1)
            digit2 = self.digitdecode(self.data, self.DIGIT2_MASK, self.DIGIT2)

            if self.mask(self.data, self.DECPOINT_MASK) == self.DECPOINT_MASK:
                windspeed = max(digit1, 0) + digit2/10
            else:
                windspeed = max(digit1, 0)*10 + digit2

            if windspeed >= 0:
                self.output.append(VWR(wind_angle, left_right, windspeed).msg)
            else:
                self.output.append(ERR('NASA WIND SPEED ERROR').msg)
