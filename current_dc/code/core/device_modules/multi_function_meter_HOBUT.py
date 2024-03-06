import traceback
import asyncio
import logging

logger = logging.getLogger(__name__)

# Total
# 0x0012 = kW sum
# 0x0014 = kVA sum
# 0x0016 = kVAR sum
# 0x001E = Hz
# 0x0018 = PF

# Per phase
# 0x0006 = v1 (phase)
# 0x0008 = v2
# 0x000A = v3
# 0x000C = I1
# 0x000E = I2
# 0x0010 = I3
# 0x0054 = THD V1
# 0x0056 = THD V2
# 0x0058 = THD V3
# 0x005A = THD I1
# 0x005C = THD I2
# 0x005E = THD I3


class HOBUT_850_LTHN:
    def __init__(self, config, variables):
        self.regkW = config.get("register_total_real_power",0x0012)
        self.regkVA = config.get("register_total_reactive_power",0x0016)
        self.regkVAR = config.get("register_total_apparent_power",0x0014)
        self.regHz = config.get("register_average_frequency",0x001E)
        self.regPF = config.get("register_average_power_factor",0x0018)

        self.regV1 = config.get("register_voltage_phase_1", 0x0006)
        self.regV2 = config.get("register_voltage_phase_2", 0x0008)
        self.regV3 = config.get("register_voltage_phase_3", 0x000A)

        self.regI1 = config.get("register_current_phase_1", 0x000C)
        self.regI2 = config.get("register_current_phase_2", 0x000E)
        self.regI3 = config.get("register_current_phase_3", 0x0010)

        self.regTHD_V1 = config.get("register_thd_V1", 0x0054)
        self.regTHD_V2 = config.get("register_thd_V2", 0x0056)
        self.regTHD_V3 = config.get("register_thd_V3", 0x0058)

        self.regTHD_I1 = config.get("register_thd_I1", 0x005A)
        self.regTHD_I2 = config.get("register_thd_I2", 0x005C)
        self.regTHD_I3 = config.get("register_thd_I3", 0x005E)

        self.slave_id = config.get("slave_id")

        self.modbus = None

        self.varkW = variables.get('power_real')
        self.varkVA = variables.get('power_reactive')
        self.varkVAR = variables.get('power_apparent')
        self.varHz = variables.get('frequency')
        self.varPF = variables.get('PF')

        self.varI1 = variables.get('I1')
        self.varI2 = variables.get('I2')
        self.varI3 = variables.get('I3')

        self.varV1 = variables.get('V1')
        self.varV2 = variables.get('V2')
        self.varV3 = variables.get('V3')

        self.varTHD_V1 = variables.get('THD_V1')
        self.varTHD_V2 = variables.get('THD_V2')
        self.varTHD_V3 = variables.get('THD_V3')

        self.varTHD_I1 = variables.get('THD_I1')
        self.varTHD_I2 = variables.get('THD_I2')
        self.varTHD_I3 = variables.get('THD_I3')

    def initialise(self, interface):
        self.modbus = interface

    async def sample(self):
        try:
            readings = {}

            if self.varI1 is not None:
                readings[self.varI1] = await self.read_modbus_register(self.regI1)
            if self.varI2 is not None:
                readings[self.varI2] = await self.read_modbus_register(self.regI2)
            if self.varI3 is not None:
                readings[self.varI3] = await self.read_modbus_register(self.regI3)

            if self.varV1 is not None:
                readings[self.varV1] = await self.read_modbus_register(self.regV1)
            if self.varV2 is not None:
                readings[self.varV2] = await self.read_modbus_register(self.regV2)
            if self.varV3 is not None:
                readings[self.varV3] = await self.read_modbus_register(self.regV3)

            if self.varTHD_V1 is not None:
                readings[self.varTHD_V1] = await self.read_modbus_register(self.regTHD_V1)
            if self.varTHD_V2 is not None:
                readings[self.varTHD_V2] = await self.read_modbus_register(self.regTHD_V2)
            if self.varTHD_V3 is not None:
                readings[self.varTHD_V3] = await self.read_modbus_register(self.regTHD_V3)

            if self.varTHD_I1 is not None:
                readings[self.varTHD_I1] = await self.read_modbus_register(self.regTHD_I1)
            if self.varTHD_I2 is not None:
                readings[self.varTHD_I2] = await self.read_modbus_register(self.regTHD_I2)
            if self.varTHD_I3 is not None:
                readings[self.varTHD_I3] = await self.read_modbus_register(self.regTHD_I3)

            if self.varkW is not None:
                readings[self.varkW] = await self.read_modbus_register(self.regkW)
            if self.varkVA is not None:
                readings[self.varkVA] = await self.read_modbus_register(self.regkVA)
            if self.varkVAR is not None:
                readings[self.varkVAR] = await self.read_modbus_register(self.regkVAR)
            if self.varHz is not None:
                readings[self.varHz] = await self.read_modbus_register(self.regHz)
            if self.varPF is not None:
                readings[self.varPF] = await self.read_modbus_register(self.regPF)

            return readings
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e
    


    async def read_modbus_register(self, register):
        result = self.modbus.read_register(register, 4, self.slave_id)
        if asyncio.iscoroutine(result):
            return await result
        else:
            return result
