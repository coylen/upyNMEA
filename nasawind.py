
COMMAND = bytearray.fromhex("C8 80 E0 F8 70")
DIRECTION_MASK = bytearray.fromhex("0F FF 0F 0F FF F0 00 F0 F0 FF 0F FF")
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


def receive(iic):
    try:
        data = iic.recv(17)
        return data
    except:
        return None


def decode(data):
    # check first five bytes of data for validity

    direction = -1
    windspeed = -1

    if data[:5] == COMMAND:
        data = data[5:]  # strip this preamble before further processing

        #
        directiondata = mask(data, DIRECTION_MASK)
        directiondata_int = int.from_bytes(directiondata, byteorder='big')
        # get direction of or standard single digit display for position of bit and corresponding position
        if bitCount(directiondata_int) == 1:
            direction = DIRECTION[lowestSet(directiondata_int)]

    return direction, windspeed

def mask(data, msk):
    if len(data) == len(msk):
        masked_data = bytearray()
        for d, m in data, msk:
            masked_data.append(d & m)

        return masked_data


def lowestSet(int_type):
    low = int_type & -int_type
    lowbit = -1
    while low:
        low >>= 1
        lowbit += 1
    return lowbit


def bitCount(int_type):
    count = 0
    while int_type:
        int_type &= int_type - 1
        count += 1
    return count
