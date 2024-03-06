from smbus2 import SMBus
from smbus2 import i2c_msg as Msg
import logging

logger = logging.getLogger(__name__)


pip_requirements = {"smbus2":"0.4.3"}

class I2C:
    def __init__(self,config):
        self.bus = config.get('bus', 1)
        self.addr = config.get('addr')
        self.i2c = SMBus()


    def initialise(self):
        self.i2c.open(self.bus)

    def read_register(self,register,num_bytes,stop=False):     # Write address, register_no  -- Read address, data
        write_reg_addr = Msg.write(self.addr,[register])
        read_reg_data = Msg.read(self.addr,num_bytes)

        if stop:
            self.i2c.i2c_rdwr(write_reg_addr)
            self.i2c.i2c_rdwr(read_reg_data)
        else:
            self.i2c.i2c_rdwr(write_reg_addr, read_reg_data)

        return list(read_reg_data)

    def write_register(self,register,data):    #Write address, register, data...
        write_reg_addr_data = Msg.write(self.addr,[register,*data])
        self.i2c.i2c_rdwr(write_reg_addr_data)