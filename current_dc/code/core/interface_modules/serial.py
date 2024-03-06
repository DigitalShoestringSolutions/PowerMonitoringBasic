import serial

pip_requirements = {"pyserial":"3.5"}


class Serial:
    PARITY = {
        "none":serial.PARITY_NONE,
        "even":serial.PARITY_EVEN,
        "odd":serial.PARITY_ODD
    }

    BYTESIZE = {
        5:serial.FIVEBITS,
        6:serial.SIXBITS,
        7:serial.SEVENBITS,
        8:serial.EIGHTBITS
    }

    STOPBITS = {
        '1':serial.STOPBITS_ONE,
        '1.5':serial.STOPBITS_ONE_POINT_FIVE,
        '2':serial.STOPBITS_TWO
    }

    def __init__(self,config):
        self.port = config['port']
        self.baudrate = config['baudrate']
        self.bytesize = config.get('bytesize',8)
        self.parity = config.get('parity','none')
        self.stopbits  = config.get('stopbits','1')
        self.exclusive = config.get('exclusive',False)

        self.serial = serial.Serial(timeout = 0.1)

    def initialise(self):
        # set up serial
        self.serial.port = self.port
        self.serial.baudrate = self.baudrate
        self.serial.bytesize = self.BYTESIZE.get(self.bytesize,serial.EIGHTBITS)
        self.serial.parity = self.PARITY.get(self.parity,serial.PARITY_NONE)
        self.serial.stopbits = self.STOPBITS.get(self.stopbits,serial.STOPBITS_ONE)
        self.serial.exclusive = self.exclusive
        # open
        self.serial.open()

    def read(self):
        return self.serial.readline()

    def write(self,data):
        self.serial.write(data)