#main control program

from NasaWind import NasaWind

def setup():
    import network
    wlan=network.WLAN(network.STA_IF)
    wlan.active(true)
    wlan.connect('Jambo','')

def connect():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.129.1',10110)) #check address
    return s

def run():
    nw = NasaWind()
    s = connect()
    while True:
        try:
            nw.update()
            s.send(nw.output)
        except:
            pass
        sleep(1)








