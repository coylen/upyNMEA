import pyb

class UART:

    def __init__(self, channel=1, baud=4800, UART_object=None, debug=False):

        if UART_object is not None:
            self.UART=UART_object
        else:
            self.UART=pyb.UART(channel, baud)
        self.debug=debug

    # standard function to write data to UART

    def send(self, output):
        # TODO: Add UART OUTPUT
        if self.debug:
            print(output)
        else:
            self.UART.write(output)