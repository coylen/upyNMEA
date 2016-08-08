import math
from pyb import I2C

class TiltCompCompass:

    ConfigurationRegisterA_A = 0x20
    ConfigurationRegisterB_A = 0x21
    ConfigurationRegisterC_A = 0x22
    ConfigurationRegisterD_A = 0x23
    ConfigurationRegisterE_A = 0x24
    ConfigurationRegisterF_A = 0x25
    StatusRegister_A = 0x27
    AxisXDataRegisterMSB_A = 0x28
    AxisXDataRegisterLSB_A = 0x29
    AxisZDataRegisterMSB_A = 0x2A
    AxisZDataRegisterLSB_A = 0x2B
    AxisYDataRegisterMSB_A = 0x2C
    AxisYDataRegisterLSB_A = 0x2D

    ConfigurationRegisterA_M = 0x00
    ConfigurationRegisterB_M = 0x01
    ModeRegister_M = 0x02
    AxisXDataRegisterMSB_M = 0x03
    AxisXDataRegisterLSB_M = 0x04
    AxisZDataRegisterMSB_M = 0x05
    AxisZDataRegisterLSB_M = 0x06
    AxisYDataRegisterMSB_M = 0x07
    AxisYDataRegisterLSB_M = 0x08
    StatusRegister_M = 0x09
    IdentificationRegisterA_M = 0x0A
    IdentificationRegisterB_M = 0x0B
    IdentificationRegisterC_M = 0x0C

    MeasurementContinuous_M = 0x00
    MeasurementSingleShot_M = 0x01
    MeasurementIdle_M = 0x03



    def __init__(self, port, magaddr=0x1e, accaddr=0x19,gauss=1.3):
    # self.bus = i2c.i2c(port, addr)
        self.bus = I2C(port, I2C.MASTER)
        self.MagAddress = magaddr
        self.AccAddress =accaddr
        self.setMagScale(gauss)
        self.setContinuousMode()
        self.setDeclination(0)
        #setup acc in basic modes
        self.setOption(self.AccAddress,self.ConfigurationRegisterA_A,0b01100111)
        self.setOption(self.AccAddress,self.ConfigurationRegisterB_A,0b00100000)

    def setContinuousMode(self):
        self.setOption(self.MagAddress,self.ModeRegister_M, self.MeasurementContinuous_M)

    def setMagScale(self, gauss):
        if gauss == 0.88:
            self.scale_reg = 0x00
            self.scale = 0.73
        elif gauss == 1.3:
            self.scale_reg = 0x01
            self.scale = 0.92
        elif gauss == 1.9:
            self.scale_reg = 0x02
            self.scale = 1.22
        elif gauss == 2.5:
            self.scale_reg = 0x03
            self.scale = 1.52
        elif gauss == 4.0:
            self.scale_reg = 0x04
            self.scale = 2.27
        elif gauss == 4.7:
            self.scale_reg = 0x05
            self.scale = 2.56
        elif gauss == 5.6:
            self.scale_reg = 0x06
            self.scale = 3.03
        elif gauss == 8.1:
            self.scale_reg = 0x07
            self.scale = 4.35
        self.scale_reg = self.scale_reg << 5
        self.setOption(self.MagAddress, self.ConfigurationRegisterB_M, self.scale_reg)

    def setDeclination(self, degree, min=0):
        self.declinationDeg = degree
        self.declinationMin = min
        self.declination = (degree + min / 60) * (math.pi / 180)

    def setOption(self, address,register, *function_set):
        options = 0x00
        for function in function_set:
            options = options | function
         # self.bus.write_byte(register, options)
        self.bus.mem_write(options, address, register)

    # Adds to existing options of register
    def addOption(self,address, register, *function_set):
        options = self.bus.mem_read(1,address,register)
        for function in function_set:
            options = options | function
        self.bus.mem_write(options, address, register)

    # Removes options of register
    def removeOption(self, address, register, *function_set):
        options = self.bus.mem_read(1,address,register)
        for function in function_set:
            options = options & (function ^ 0b11111111)
        self.bus.mem_write(options, address, register)

    def getDeclination(self):
        return (self.declinationDeg, self.declinationMin)

    def getDeclinationString(self):
        return str(self.declinationDeg) + "\u00b0 " + str(self.declinationMin) + "'"

    # Returns heading in degrees and minutes
    def getHeading(self):
        (scaled_x, scaled_y, scaled_z) = self.getAxes()
        headingRad = math.atan2(scaled_y, scaled_x)
        headingRad += self.declination
        # Correct for reversed heading
        if (headingRad < 0):
            headingRad += 2 * math.pi
        # Check for wrap and compensate
        if (headingRad > 2 * math.pi):
            headingRad -= 2 * math.pi
        # Convert to degrees from radians
        headingDeg = headingRad * 180 / math.pi
        degrees = math.floor(headingDeg)
        minutes = round(((headingDeg - degrees) * 60))
        return (degrees, minutes)

    def getHeadingString(self):
        (degrees, minutes) = self.getHeading()
        return str(degrees) + "\u00b0 " + str(minutes) + "'"

    def getAxes(self):
        (magno_x, magno_z, magno_y) = self.read_3s16int(self.MagAddress,self.AxisXDataRegisterMSB_M)
        if (magno_x == -4096):
            magno_x = None
        else:
            magno_x = round(magno_x * self.scale, 4)
        if (magno_y == -4096):
            magno_y = None
        else:
            magno_y = round(magno_y * self.scale, 4)
        if (magno_z == -4096):
            magno_z = None
        else:
            magno_z = round(magno_z * self.scale, 4)
        return (magno_x, magno_y, magno_z)

    def read_3s16int(self,address, register, flip = False):
        #data = self.i2c_device.transaction(
        #    writing_bytes(self.addr, register),
        #    reading(self.addr, 6))[0]
        data=self.bus.mem_read(6,address,register)
       # if self.debug:
        #    print("3 signed 16: %s " % ', '.join(map(hex, data)))
        if flip:
            s_int1 = (data[1] << 8) | data[0]
        else:
            s_int1 = (data[0] << 8) | data[1]
        if flip:
            s_int2 = (data[3] << 8) | data[2]
        else:
            s_int2 = (data[2] << 8) | data[3]
        if flip:
            s_int3 = (data[5] << 8) | data[4]
        else:
            s_int3 = (data[4] << 8) | data[5]
        return (self.twosToInt(s_int1, 16), self.twosToInt(s_int2, 16), self.twosToInt(s_int3, 16) )

    def twosToInt(self, val, len):
        # Convert twos compliment to integer
        if(val & (1 << len - 1)):
            val = val - (1<<len)
       # if self.debug:
       #     print(str(val))
        return val

    def getAccAxes(self):
        (magno_x, magno_z, magno_y) = self.read_3s16int(self.AccAddress,self.AxisXDataRegisterMSB_A)
        if (magno_x == -4096):
            magno_x = None
        else:
            magno_x = round(magno_x * self.scale, 4)
        if (magno_y == -4096):
            magno_y = None
        else:
            magno_y = round(magno_y * self.scale, 4)
        if (magno_z == -4096):
            magno_z = None
        else:
            magno_z = round(magno_z * self.scale, 4)
        return (magno_x, magno_y, magno_z)

#test for scaling of LSM303

def test():
    a = TiltCompCompass(1)
    a.lsm.setDeclination(0)
    a.lsm.setContinuousMode()
    valid = False
    while valid == False:
        b=a.getAxes()
        print("Data {}".format(b))
        valid = True
        for x in b:
            if x is None:
                valid = False
                if a.scale_reg < 7:
                    a.scale_reg += 1
                else:
                    print("BUGGERED")

    print(a.scale_reg)


