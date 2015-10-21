import pyb

ratio = 1


def pulse(frq):
    timer = pyb.Timer(14, freq=frq)
    ch2 = timer.channel(1, pyb.Timer.PWM, pin=pyb.Pin.board.X8, pulse_width=(timer.period+1)*frq/100)


def speed(knots):
    global ratio
    pulse(1/ratio*knots)


def setup():
    return pyb.I2C(2, pyb.I2C.SLAVE, addr=0x3E)


def rec(i2c):
    try:
        i2c.recv(17)
    except:
        print("FAIL")


print("nasawind capture")
print("")
print("first call pulse(1)")
print("set ratio= displayed speed")
print(" for future edit file to hardcode ratio into file")
print("call speed(knots)")
print("call a=setup()")
print("call rec(a) whilst tweaking options")

