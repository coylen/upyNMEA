# upower.py Enables access to functions useful in low power Pyboard projects
# Copyright 2015 Peter Hinch
# This code is released under the MIT licence

# V0.3 13th February 2016

# http://www.st.com/web/en/resource/technical/document/application_note/DM00025071.pdf
import pyb, stm, os,  uctypes

# CODE RUNS ON IMPORT **** START ****

def buildcheck(tupTarget):
    fail = True
    if 'uname' in dir(os):
        datestring = os.uname()[3]
        date = datestring.split(' on')[1]
        idate = tuple([int(x) for x in date.split('-')])
        fail = idate < tupTarget
    if fail:
        raise OSError('This driver requires a firmware build dated {:4d}-{:02d}-{:02d} or later'.format(*tupTarget))

buildcheck((2016, 02, 11))                      # Version allows 32 bit write to stm register

usb_connected = False
if pyb.usb_mode() is not None:                  # User has enabled CDC in boot.py
    usb_connected = pyb.Pin.board.USB_VBUS.value() == 1
    if not usb_connected:
        pyb.usb_mode(None)                      # Save power

# CODE RUNS ON IMPORT **** END ****

def bounds(val, minval, maxval, msg):           # Bounds check
    if not (val >= minval and val <= maxval):
        raise ValueError(msg)

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class RTCError(OSError):
    pass

def cprint(*args, **kwargs):                    # Conditional print: USB fails if low power modes are used
    global usb_connected
    if not usb_connected:                       # assume a UART has been specified in boot.py
        print(*args, **kwargs)

#@micropython.asm_thumb
#def ctz(r0):                                    # Count the trailing zeros in an integer
#    rbit(r0, r0)
#    clz(r0, r0)

def ctz(n): # Now in Python to enable frozen bytecode
    if not n:
        return 32
    count = 0
    while not n & 1:
        n >>= 1
        count += 1
    return count

# ***** BACKUP RAM SUPPORT *****

@singleton
class BkpRAM(object):
    BKPSRAM = 0x40024000
    def __init__(self):
        stm.mem32[stm.RCC + stm.RCC_APB1ENR] |= 0x10000000 # PWREN bit
        stm.mem32[stm.PWR + stm.PWR_CR] |= 0x100  # Set the DBP bit in the PWR power control register
        stm.mem32[stm.RCC +stm.RCC_AHB1ENR]|= 0x40000 # enable BKPSRAMEN
        stm.mem32[stm.PWR + stm.PWR_CSR] |= 0x200 # BRE backup register enable bit
        self._ba = uctypes.bytearray_at(self.BKPSRAM, 4096)
    def idxcheck(self, idx):
        bounds(idx, 0, 0x3ff, 'RTC backup RAM index out of range')
    def __getitem__(self, idx):
        self.idxcheck(idx)
        return stm.mem32[self.BKPSRAM + idx * 4]
    def __setitem__(self, idx, val):
        self.idxcheck(idx)
        stm.mem32[self.BKPSRAM + idx * 4] = val
    @property
    def ba(self):
        return self._ba                         # Access as bytearray

# ***** RTC REGISTERS *****

@singleton
class RTCRegs(object):
    def idxcheck(self, idx):
        bounds(idx, 0, 19, 'RTC register index out of range')
    def __getitem__(self, idx):
        self.idxcheck(idx)
        return stm.mem32[stm.RTC + stm.RTC_BKP0R+ idx * 4]
    def __setitem__(self, idx, val):
        self.idxcheck(idx)
        stm.mem32[stm.RTC + stm.RTC_BKP0R + idx * 4] = val

# Return the reason for a wakeup event. Note that boot detection uses the last word of backup RAM.
def why():
    result = None
    bkpram = BkpRAM()
    if stm.mem32[stm.PWR+stm.PWR_CSR] & 2 == 0:
        if bkpram[1023] != 0x27288a6f:
            result = 'BOOT'
            bkpram[1023] = 0x27288a6f                       # In case a backup battery is in place
        else:
            result = 'POWERUP'                              # a backup battery is in place
    else:
        rtc_isr = stm.mem32[stm.RTC + stm.RTC_ISR]
        if rtc_isr & 0x2000:
            result = 'TAMPER'
        elif rtc_isr & 0x400:
            result = 'WAKEUP'
        elif rtc_isr & 0x200:
            stm.mem32[stm.RTC + stm.RTC_ISR] |= 0x200
            result = 'ALARM_B'
        elif rtc_isr & 0x100 :
            stm.mem32[stm.RTC + stm.RTC_ISR] |= 0x100
            result = 'ALARM_A'
        elif stm.mem32[stm.PWR + stm.PWR_CSR] & 1:          # WUF set: the only remaining cause is X1 (?)
            result = 'X1'                                   # if WUF not set, cause unknown, return None
    stm.mem32[stm.PWR + stm.PWR_CR] |= 4                    # Clear the PWR Wakeup (WUF) flag
    return result


def adcread(chan):                              # 16 temp 17 vbat 18 vref
    bounds(chan, 16, 18, 'Invalid ADC channel')
    start = pyb.millis()
    timeout = 100
    stm.mem32[stm.RCC + stm.RCC_APB2ENR] |= 0x100 # enable ADC1 clock.0x4100
    stm.mem32[stm.ADC1 + stm.ADC_CR2] = 1       # Turn on ADC
    stm.mem32[stm.ADC1 + stm.ADC_CR1] = 0       # 12 bit
    if chan == 17:
        stm.mem32[stm.ADC1 + stm.ADC_SMPR1] = 0x200000 # 15 cycles channel 17
        stm.mem32[stm.ADC + 4] = 1 << 23
    elif chan == 18:
        stm.mem32[stm.ADC1 + stm.ADC_SMPR1] = 0x1000000 # 15 cycles channel 18 0x1200000
        stm.mem32[stm.ADC + 4] = 0xc00000
    else:
        stm.mem32[stm.ADC1 + stm.ADC_SMPR1] = 0x40000 # 15 cycles channel 16
        stm.mem32[stm.ADC + 4] = 1 << 23
    stm.mem32[stm.ADC1 + stm.ADC_SQR3] = chan
    stm.mem32[stm.ADC1 + stm.ADC_CR2] = 1 | (1 << 30) | (1 << 10) # start conversion
    while not stm.mem32[stm.ADC1 + stm.ADC_SR] & 2: # wait for EOC
        if pyb.elapsed_millis(start) > timeout:
            raise OSError('ADC timout')
    data = stm.mem32[stm.ADC1 + stm.ADC_DR]     # clears down EOC
    stm.mem32[stm.ADC1 + stm.ADC_CR2] = 0       # Turn off ADC
    return data

def v33():
    return 4096 * 1.21 / adcread(17)

def vbat():
    return  1.21 * 2 * adcread(18) / adcread(17)  # 2:1 divider on Vbat channel

def vref():
    return 3.3 * adcread(17) / 4096

def temperature():
    return 25 + 400 * (3.3 * adcread(16) / 4096 - 0.76)

