from serialconnector import SerialConnector

def write_response(ser, cmd):
    try:
        ser.write(cmd)
    except:
        # print("WARNING: Could not send trigger to Sponge. Is sponge connected?")
        pass

class Sponge(SerialConnector):
    def __init__(self, nrows=4, ncols=4, **kwargs):
        self.nrows = nrows
        self.ncols = ncols
        self.motors = list(range(nrows*ncols))

        super(Sponge, self).__init__(**kwargs)

    def start(self):
        write_response(self.ser, chr(200))

    def end(self):
        write_response(self.ser, chr(255))

    def motor_on(self, motor, intensity):
        write_response(self.ser, chr(motor))
        write_response(self.ser, chr(intensity))

    def motor_off(self, motor):
        write_response(self.ser, chr(motor))
        write_response(self.ser, chr(0))

    def stop_all(self):
        # Turn all motors off
        self.start()
        for motor in range(self.nrows*self.ncols):
            if motor in motors:
                self.motor_off(motor)
        self.end()
