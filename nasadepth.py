
#
#     NASAClipper_I2C_to_NMEA v0.5
#     Decode the NASA Clipper Data into a NMEA compatible serial string
#
#     Python code based on Arduino Sketches
#     written by Peter Holtermann
#     with additions from Victor Klein
#
#
#
#     This software is distributed under the GPL v3.0 License
#
#
#     At the back of your NASA Clipper should be a round connector
#     with 5 pins, looking roughly like this ASCII art:
#       Pin Location          Pin Number
#           |                     2
#       \       /              4     5
#     -           -          1         3
#
#           O                     6
#
#   Pin 1: SCL
#   Pin 2: GND
#   Pin 3: SDA
#   Pin 4: 12V
#   Pin 5: GND
#
#   For Detail refer also to:
#
#   http://wiki.openseamap.org/wiki/De:NASA_Clipper_Range
#
#   If you connect SCL, SDA and GND with your arduino
#   and upload this sketch you should get the depth
#   information as serial data.
#
#
# // The NASA Clipper sends a 12 byte I2C data packet, this data is directly send to a pcf8566p
# // LCD Driver. The first byte is the address and the write direction, the next eleven bytes is data.
# // The first 5 bytes is a command, the proceeding 6 bytes are data
# // positions and contain the single LCD elements.
# // Example data {0x7c,0xce,0x80,0xe0,0xf8,0x70,0x00,0x00,0x00,0x00,0x00,0x00};
# //               addr   0    1    2    3    4    5    6    7    8    9    10
# //                      com  com  com com   com dta  dta  dta  dta  dta  dta
# // Example depth  : 23.3
# // Digit number   : 12.3

from nasa import NASA
from nmeagenerator import DPT


class NASADepth(NASA):

    def __init__(self, i2c, pin, pin_value):
        super().__init__(i2c, pin, pin_value)
        self.packet_size = 11

    COMMAND = bytes(b'\xCE\x80\xE0\xF8\x70')
    DEPTH_MASK = bytes(b'\x01\x00\x00\x00\x00\x00')
    DECPOINT_MASK = bytes(b'\x00\x00\x00\x80\x00\x00')
    METRES_MASK = bytes(b'\x00\x00\x00\x40\x00\x00')
    DIGIT1_MASK = bytes(b'\x00\x00\x00\x00\x2F\xC0')
    DIGIT2_MASK = bytes(b'\xFE\x00\x00\x00\x00\x00')
    DIGIT3_MASK = bytes(b'\x00\xBF\x00\x00\x00\x00')

    DIGIT3 = [bytes(b'\x00\xBB\x00\x00\x00\x00'),
              bytes(b'\x00\x11\x00\x00\x00\x00'),
              bytes(b'\x00\x9E\x00\x00\x00\x00'),
              bytes(b'\x00\x97\x00\x00\x00\x00'),
              bytes(b'\x00\x35\x00\x00\x00\x00'),
              bytes(b'\x00\xA7\x00\x00\x00\x00'),
              bytes(b'\x00\xAF\x00\x00\x00\x00'),
              bytes(b'\x00\x91\x00\x00\x00\x00'),
              bytes(b'\x00\xBF\x00\x00\x00\x00'),
              bytes(b'\x00\xB7\x00\x00\x00\x00')]

    DIGIT2 = [bytes(b'\xEE\x00\x00\x00\x00\x00'),
              bytes(b'\x44\x00\x00\x00\x00\x00'),
              bytes(b'\xB6\x00\x00\x00\x00\x00'),
              bytes(b'\xD6\x00\x00\x00\x00\x00'),
              bytes(b'\x5C\x00\x00\x00\x00\x00'),
              bytes(b'\xDA\x00\x00\x00\x00\x00'),
              bytes(b'\xFA\x00\x00\x00\x00\x00'),
              bytes(b'\x46\x00\x00\x00\x00\x00'),
              bytes(b'\xFE\x00\x00\x00\x00\x00'),
              bytes(b'\xDE\x00\x00\x00\x00\x00')]

    DIGIT1 = [bytes(b'\x00\x00\x00\x00\x2E\xc0'),
              bytes(b'\x00\x00\x00\x00\x04\x40'),
              bytes(b'\x00\x00\x00\x00\x27\x80'),
              bytes(b'\x00\x00\x00\x00\x25\xC0'),
              bytes(b'\x00\x00\x00\x00\x0D\x40'),
              bytes(b'\x00\x00\x00\x00\x29\xC0'),
              bytes(b'\x00\x00\x00\x00\x2B\xC0'),
              bytes(b'\x00\x00\x00\x00\x24\x40'),
              bytes(b'\x00\x00\x00\x00\x2F\xC0'),
              bytes(b'\x00\x00\x00\x00\x2D\xC0')]


    def decode(self):
        # check first five bytes of data for validity
        # depth = False
        # metres = False
        # decimal_point = False

        digit1 = -1
        digit2 = -1
        digit3 = -1

        if self.data[:5] == self.COMMAND:
            self.data = self.data[5:]  # strip this preamble before further processing

            # check for validity and process data if valid
            if (self.mask(self.data, self.DEPTH_MASK) == self.DEPTH_MASK &
                    self.mask(self.data, self.METRES_MASK) == self.METRES_MASK):

                digit1 = self.digitdecode(self.data, self.DIGIT1_MASK, self.DIGIT1)
                digit2 = self.digitdecode(self.data, self.DIGIT2_MASK, self.DIGIT2)
                digit3 = self.digitdecode(self.data, self.DIGIT3_MASK, self.DIGIT3)

            if self.mask(self.data, self.DECPOINT_MASK) == self.DECPOINT_MASK:
                depth = max(digit1, 0)*10 + digit2 + digit3/10
            else:
                depth = max(digit1, 0)*100 + digit2*10 + digit3

            if depth > 0:
                self.output += DPT(depth, 0)
                return depth
