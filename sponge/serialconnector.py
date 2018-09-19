import serial
import sys
import glob
import time

class SerialConnector(object):
    """"""
    def __init__(self, device=None):

        self.get_devices()

        if device in self.available_devices:
            self.device = device
        elif device is "test":
            self.device = device
        else:
            self.device = None


    def get_devices(self):
        """List all devices"""

        # First get the platform, to determine
        # device names.
        if sys.platform.startswith("win"):
            # Create device names for Windows
            devices = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux'):
            # Create device names for Linux "/dev/tty"
            devices = glob.glob('/dev/ttyACM*')
        elif sys.platform.startswith('darwin'):
            # Create device names for Apple
            devices = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError

        self.available_devices = []
        for device in devices:
            try:
                s = serial.Serial(device)
                s.close()
                self.available_devices.append(device)
            except (OSError, serial.SerialException):
                pass


    def connect(self):
        """Connect to device"""

        if self.device is None:
        # Print all devices
            print("Select a device:")
            for i, device in enumerate(self.available_devices):
                print("%d: %s" %(i, device))

            # Ask user to select device.
            device = input("Enter number: ")
            self.device = self.available_devices[int(device)]

        if self.device is "test":
            self.ser = None
            print("Testing. Not connected to any device.")
        else:
            # Connect to device, baudrate 115200?
            self.ser = serial.Serial(self.device, 115200)
            print("Connected to %s." % self.device)

            # Wait a bit
            time.sleep(1)

    def close(self):
        if self.ser is not None:
            self.ser.close()
