import os
import logging

logger = logging.getLogger(__name__)

class OneWire:
    BASE_PATH='/sys/bus/w1/devices/'
    def __init__(self,config):
        self.sensor_id = config.get('sensor_id', None)
        self.filename = config.get('filename',"w1_slave")

        
        if self.sensor_id is not None:
            self.sensor_filepath = os.path.join(self.BASE_PATH,self.sensor_id,self.filename)
        else: # If sensor not specified - auto detect the first sensor
            with os.scandir(self.BASE_PATH) as file_iterator:
                for file in file_iterator:
                    print(file)
                    # if file matches:
                    #     self.sensor_filepath = file

        


    def initialise(self):
        if not os.path.exists(self.sensor_filepath):
            logger.error(f"One wire device not found at {self.sensor_filepath}")

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