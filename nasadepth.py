
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

    COMMAND = bytearray.fromhex("CE 80 E0 F8 70")
    DEPTH_MASK = bytearray.fromhex("01 00 00 00 00 00")
    DECPOINT_MASK = bytearray.fromhex("00 00 00 80 00 00")
    METRES_MASK = bytearray.fromhex("00 00 00 40 00 00")
    DIGIT1_MASK = bytearray.fromhex("00 00 00 00 2F C0")
    DIGIT2_MASK = bytearray.fromhex("FE 00 00 00 00 00")
    DIGIT3_MASK = bytearray.fromhex("00 BF 00 00 00 00")

    DIGIT3 = [bytearray.fromhex("00 bb 00 00 00 00"),
              bytearray.fromhex("00 11 00 00 00 00"),
              bytearray.fromhex("00 9e 00 00 00 00"),
              bytearray.fromhex("00 97 00 00 00 00"),
              bytearray.fromhex("00 35 00 00 00 00"),
              bytearray.fromhex("00 a7 00 00 00 00"),
              bytearray.fromhex("00 af 00 00 00 00"),
              bytearray.fromhex("00 91 00 00 00 00"),
              bytearray.fromhex("00 bf 00 00 00 00"),
              bytearray.fromhex("00 b7 00 00 00 00")]

    DIGIT2 = [bytearray.fromhex("ee 00 00 00 00 00"),
              bytearray.fromhex("44 00 00 00 00 00"),
              bytearray.fromhex("b6 00 00 00 00 00"),
              bytearray.fromhex("d6 00 00 00 00 00"),
              bytearray.fromhex("5c 00 00 00 00 00"),
              bytearray.fromhex("da 00 00 00 00 00"),
              bytearray.fromhex("fa 00 00 00 00 00"),
              bytearray.fromhex("46 00 00 00 00 00"),
              bytearray.fromhex("fe 00 00 00 00 00"),
              bytearray.fromhex("de 00 00 00 00 00")]

    DIGIT1 = [bytearray.fromhex("00 00 00 00 2e c0"),
              bytearray.fromhex("00 00 00 00 04 40"),
              bytearray.fromhex("00 00 00 00 27 80"),
              bytearray.fromhex("00 00 00 00 25 c0"),
              bytearray.fromhex("00 00 00 00 0d 40"),
              bytearray.fromhex("00 00 00 00 29 c0"),
              bytearray.fromhex("00 00 00 00 2b c0"),
              bytearray.fromhex("00 00 00 00 24 40"),
              bytearray.fromhex("00 00 00 00 2f c0"),
              bytearray.fromhex("00 00 00 00 2d c0")]

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
