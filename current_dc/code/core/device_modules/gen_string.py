import json
import re
import jsonpath_rw
import traceback
import logging

logger = logging.getLogger(__name__)


class SerialJSON:
    def __init__(self, config, variables):
        self.spec = config.get('spec',None)
        self.serial = None

    def initialise(self, interface):
        self.serial = interface

    def sample(self):
        try:
            # get string from serial
            raw_string = self.serial.read()
            string = raw_string.decode('utf-8').strip()
            cleaned_string = re.sub(r'(0x\d\d)',r'"\1"',string)
            json_dict = json.loads(cleaned_string)
            if self.spec:
                out = {}
                for key,value in self.spec.items():
                    found = jsonpath_rw.parse(value).find(json_dict)
                    if len(found)>0:
                        out[key] = found[0].value
                return out
            else:
                return json_dict
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e
