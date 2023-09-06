# ----------------------------------------------------------------------
#
#    Power Monitoring (Basic solution) -- This digital solution measures,
#    reports and records both AC power and current consumed by an electrical 
#    equipment, so that its energy consumption can be understood and 
#    taken action upon. This version comes with one current transformer 
#    clamp of 20A that is buckled up to the electric line the equipment 
#    is connected to. The solution provides a Grafana dashboard that 
#    displays current and power consumption, and an InfluxDB database 
#    to store timestamp, current and power. 
#
#    Copyright (C) 2022  Shoestring and University of Cambridge
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see https://www.gnu.org/licenses/.
#
# ----------------------------------------------------------------------

# Check config file is valid
# create BBs
# plumb BBs together
# start BBs
# monitor tasks

# packages
import tomli
import time
import logging
import zmq
# local
import measure
import wrapper
import os


logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO)  # move to log config file using python functionality

def load_config_files(directory):
    config_files = []
    for item in os.listdir(directory):
        if item.endswith(".toml"):
            file_path = os.path.join(directory, item)
            logger.info(file_path)
            with open(file_path, "rb") as file:
                config = tomli.load(file)
                config_files.append(config)
    return config_files


def get_config():
    with open("./config/config.toml", "rb") as f:
        toml_conf = tomli.load(f)
    logger.info(f"config:{toml_conf}")
    return toml_conf


def config_valid(config):
    return True


def create_building_blocks(config):
    bbs = {}

    measure_out = {"type": zmq.PUSH, "address": "tcp://127.0.0.1:4000", "bind": True}
    wrapper_in = {"type": zmq.PULL, "address": "tcp://127.0.0.1:4000", "bind": False}

    bbs["measure"] = measure.CurrentMeasureBuildingBlock(config, measure_out)
    bbs["wrapper"] = wrapper.MQTTServiceWrapper(config, wrapper_in)

    logger.debug(f"bbs {bbs}")
    return bbs


def start_building_blocks(bbs):
    for key in bbs:
        p = bbs[key].start()


def monitor_building_blocks(bbs):
    while True:
        time.sleep(1)
        for key in bbs:
            # logger.debug(f"{bbs[key].exitcode}, {bbs[key].is_alive()}")
            # todo actually monitor
            pass


if __name__ == "__main__":
    conf_arr = load_config_files("./config")
    
   # conf = get_config()
    for conf in conf_arr:
        logger.info(conf)
        # todo set logging level from config file
        if config_valid(conf):
            bbs = create_building_blocks(conf)
            start_building_blocks(bbs)
            monitor_building_blocks(bbs)
        else:
            raise Exception("bad config")
