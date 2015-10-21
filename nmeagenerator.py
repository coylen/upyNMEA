#Python classes to generate NMEA sentences
#based on Pynmea by Becky Lewis but simplified as only limited number of sentences to be created
#sentences include:
#Speed through water VHW
#Trip distance VLW
#Heading HDG
#Wind VWR
#Depth DBT/DPT
#Barometric pressure MDA
#Timestamp ZDA
#
#Talker definition will be UP - microprocessor controller

#Base NMEA Sentence Class
# used to append checksums in
# sentence generation to avoid repetition
class NMEASentence:
    def __init__(self):
        str=checksum_calc(self.msg)
        self.msg+="*"+str

# VHW Water Speed and Heading
#         1  2  3  4   5 6  7  8 9
#         |  |  |  |   | |  |  | |
# $--VHW,x.x,T,x.x,M,x.x,N,x.x,K*hh
# 1) Degress True
# 2) T = True
# 3) Degrees Magnetic
# 4) M = Magnetic
# 5) Knots (speed of vessel relative to the water)
# 6) N = Knots
# 7) Kilometers (speed of vessel relative to the water)
# 8) K = Kilometres
# 9) Checksum

class VHW(NMEASentence):
    def __init__(self, STW):
        self.msg="$UPVHW,,,,,{0},N,,".format(STW)
  #      str=checksum_calc(self.msg)
   #     self.msg+="*"+str
        super(VHW,self).__init__()

# VLW Distance Traveled through Water
#         1  2  3  4 5
#         |  |  |  | |
# $--VLW,x.x,N,x.x,N*hh
# 1) Total cumulative distance
# 2) N = Nautical Miles
# 3) Distance since Reset
# 4) N = Nautical Miles
# 5) Checksum

class VLW(NMEASentence):
    def __init__(self,distance_since_reset):
        self.msg="$UPVLW,,,{0},N".format(distance_since_reset)
        super(VLW,self).__init__()


# HDG Heading – Deviation & Variation
#         1   2  3  4  5 6
#         |   |  |  |  | |
# $--HDG,x.x,x.x,a,x.x,a*hh
# 1) Magnetic Sensor heading in degrees
# 2) Magnetic Deviation, degrees
# 3) Magnetic Deviation direction, E = Easterly, W = Westerly
# 4) Magnetic Variation degrees
# 5) Magnetic Variation direction, E = Easterly, W = Westerly
# 6) Checksum

class HDG(NMEASentence):
    def __init__(self,degree_magnetic):
        self.msg="$UPHDG,{0},1.25,W,,".format(degree_magnetic)
        super(HDG,self).__init__()


# VWR Relative Wind Speed and Angle
#         1  2  3  4  5  6  7  8 9
#         |  |  |  |  |  |  |  | |
# $--VWR,x.x,a,x.x,N,x.x,M,x.x,K*hh
# 1) Wind direction magnitude in degrees
# 2) Wind direction Left/Right of bow
# 3) Speed
# 4) N = Knots
# 5) Speed
# 6) M = Meters Per Second
# 7) Speed
# 8) K = Kilometers Per Hour
# 9) Checksum

class VWR(NMEASentence):
    def __init__(self,wind_angle,left_right,wind_speed_K):
        self.msg="$UPVWR,{0},{1},{2},N,,,,".format(wind_angle,left_right,wind_speed_K)
        super(VWR,self).__init__()


# DPT Depth of Water
#         1   2  3
#         |   |  |
# $--DPT,x.x,x.x*hh
# 1) Depth, meters
# 2) Offset from transducer;
#  positive means distance from transducer to water line,
#  negative means distance from transducer to keel
# 3) Checksum

class DPT(NMEASentence):
    def __init__(self,depth,offset):
        self.msg="$UPDPT,{0},{1}".format(depth,offset)
        super(DPT,self).__init__()


# ZDA Time & Date – UTC, Day, Month, Year and Local Time Zone
#            1      2 3   4   5  6  7
#            |      | |   |   |  |  |
# $--ZDA,hhmmss.ss,xx,xx,xxxx,xx,xx*hh
# 1) Time (UTC)
# 2) Day, 01 to 31
# 3) Month, 01 to 12
# 4) Year
# 5) Local zone minutes description, same sign as local hours
# 6) Local zone description, 00 to +/- 13 hours
# 7) Checksum

# MDA - Meteorological Composite
# The use of $--MTW, $--MWV and $--XDR is recommended.
#         1  2  3  4  5  6  7  8  9  10  11 12 13 14 15 16 17 18 19 20 21
#         |  |  |  |  |  |  |  |  |   |   |  |  |  |  |  |  |  |  |  | |
# $--MDA,x.x,I,x.x,B,x.x,C,x.x,C,x.x,x.x,x.x,C,x.x,T,x.x,M,x.x,N,x.x,M*hh
# 1) Barometric pressure, inches of mercury
# 2) Inches of mercury
# 3) Barometric pressure, bars
# 4) Bars
# 5) Air temperature, degrees C
# 6) Degrees C
# 7) Water temperature, degrees C
# 8) Degrees C
# 9) Relative humidity, percent
# 10)Absolute humidity, percent
# 11)Dew point, degrees C
# 12)Degrees C
# 13)Wind direction, degrees True
# 14)Degrees True
# 15)Wind direction, degrees Magnetic
# 16)Degrees Magnetic
# 17)Wind speed, knots
# 18)Knots
# 19)Wind speed, meters/second
# 20)Meters/second
# 21) Checksum

class MDA(NMEASentence):
    def __init__(self,depth,offset):
        self.msg="$UPMDA,,,{0},B,,,,,,,,,,,,,,,,".format(depth,offset)
        super(MDA,self).__init__()



def checksum_calc(nmea_str):
    """ Loop through all of the given characters and xor the current to the
        previous (cumulatively).
    """
    chksum_val = 0
    nmea_str = nmea_str.replace('$', '')
#    nmea_str = nmea_str.split('*')[0]
    for next_char in nmea_str:
        chksum_val ^= ord(next_char)

    return "%02X" % chksum_val


