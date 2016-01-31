from nasa import NASA
from nmeagenerator import VWR


class NASAWind(NASA):

    def __init__(self, i2c_object=None, side_str=None, pin=None, pin_value=None):
        super().__init__(i2c_object, side_str, pin, pin_value)
        self.packet_size = 17

    COMMAND = bytes(b'\xC8\x80\xE0\xF8\x70')
    DIRECTION_MASK = bytes(b'\x0F\xFF\x0F\x0F\xFF\xF0\x00\xF0\xF0\xFF\x0F\xFF')
    DIRECTION = {0: 246, 1: 258, 2: 252, 3: 264, 4: 240, 5: 228, 6: 234, 7: 222,
                 8: 288, 9: 276, 10: 282, 11: 270,
                 16: 294, 17: 306, 18: 300, 19: 312, 20: 336, 21: 324, 22: 330, 23: 318,
                 28: 198, 29: 210, 30: 204, 31: 216,
                 36: -1, 37: 186, 38: 192, 39: 180,
                 52: 342, 53: 354, 54: 348, 55: 0,
                 56: 78, 57: 90, 58: 84, 59: 96, 60: 72, 61: 60, 62: 66, 63: 54,
                 64: 30, 65: 42, 66: 36, 67: 48,
                 72: 24, 73: 12, 74: 18, 75: 6,
                 80: 102, 81: 114, 82: 108, 83: 120, 84: 144, 85: 132, 86: 138, 87: 126,
                 88: 150, 89: 168, 90: 156, 91: 174}

    def decode(self):
        # set data with error values
        direction = -1
        windspeed = -1

        # check first five bytes of data for validity
        if self.data[:5] == self.COMMAND:
            self.data = self.data[5:]  # strip this preamble before further processing

            directiondata = self.mask(self.data, self.DIRECTION_MASK)
            directiondata_int = int.from_bytes(directiondata, byteorder='big')
            # get direction of or standard single digit display for position of bit and corresponding position
            if self.bitCount(directiondata_int) == 1:
                direction = self.DIRECTION[self.lowestSet(directiondata_int)]
                if direction >= 180:
                    wind_angle = abs(direction - 360)
                    left_right = 'L'
                elif direction > 0:
                    wind_angle = direction
                    left_right = 'R'

        self.output += VWR(wind_angle, left_right, windspeed)
