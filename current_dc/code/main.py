# packages
import signal
import tomli
import time
import logging
import argparse
import zmq
import sys
import os
# local
import measure
import mqtt_out

logger = logging.getLogger("main")
terminate_flag = False


def get_config(arg_filename):
    attempt_list = [('./config/config.toml', 'defaults')]

    if arg_filename:
        attempt_list.insert(0, (arg_filename, "cmd line args"))

    env_conf_file = os.getenv("DCSM_CONFIG")
    if env_conf_file:
        attempt_list.insert(0, (env_conf_file, "environment variable"))

    for filename, src in attempt_list:
        try:
            config = do_get_config(filename)
            logger.info(f'Loaded config file "{filename}" specified in {src}')
            return config
        except FileNotFoundError:
            logger.error(
                f'File Not Found - unable to load config file "{filename}" specified in {src}. Falling back to next option.')
    logger.critical('No valid config file found! Exiting now.')
    sys.exit(255)

def do_get_config(filename):
    with open(filename, "rb") as f:
        toml_conf = tomli.load(f)
    logger.debug(f"config: {toml_conf}")
    return toml_conf


def config_valid(config):
    return True


def create_building_blocks(config):
    bbs = {}

    measure_out = {"type": zmq.PUSH, "address": "tcp://127.0.0.1:4000", "bind": True}
    wrapper_in = {"type": zmq.PULL, "address": "tcp://127.0.0.1:4000", "bind": False}

    bbs["measure"] = {"class": measure.BuildingBlockFramework, "args": [config, measure_out]}
    bbs["wrapper"] = {"class": mqtt_out.MQTTServiceWrapper, "args": [config, wrapper_in]}

    logger.debug(f"bbs {bbs}")
    return bbs


def start_building_blocks(bbs):
    for key in bbs:
        start_building_block(bbs[key])


def start_building_block(bb):
    cls = bb['class']
    args = bb['args']

    process = cls(*args)

    process.start()
    bb['process'] = process


def monitor_building_blocks(bbs):
    while True:
        time.sleep(1)
        if terminate_flag:
            logger.info("Terminating gracefully")
            for key in bbs:
                process = bbs[key]['process']
                process.join()
            return

        for key in bbs:
            process = bbs[key]['process']
            if process.is_alive() is False:
                logger.warning(f"Building block {key} stopped with exit: {process.exitcode}")
                logger.info(f"Restarting Building block {key}")
                start_building_block(bbs[key])


def graceful_signal_handler(sig, _frame):
    logger.info(f'Received {signal.Signals(sig).name}. Triggering graceful termination.')
    # todo handle gracefully
    global terminate_flag
    terminate_flag = True
    signal.alarm(10)


def harsh_signal_handler(sig, _frame):
    logger.debug(f'Received {signal.Signals(sig).name}.')
    if terminate_flag:
        logger.error(f'Failed to terminate gracefully before timeout - hard terminating')
        sys.exit(0)


def handle_args():
    levels = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}
    parser = argparse.ArgumentParser(description='Validate config file for sensing data collection service module.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--log", choices=['debug', 'info', 'warning', 'error'], help="Log level", default='info',
                        type=str)
    parser.add_argument("--config", help="Config file", type=str)
    args = parser.parse_args()

    log_level = levels.get(args.log, logging.INFO)
    conf_file = args.config

    return conf_file, log_level


if __name__ == "__main__":
    conf_file, log_level = handle_args()
    logging.basicConfig(level=log_level)
    conf = get_config(conf_file)
    signal.signal(signal.SIGINT, graceful_signal_handler)
    signal.signal(signal.SIGTERM, graceful_signal_handler)
    signal.signal(signal.SIGALRM, harsh_signal_handler)
    if config_valid(conf):
        bbs = create_building_blocks(conf)
        start_building_blocks(bbs)
        monitor_building_blocks(bbs)
    else:
        raise Exception("bad config")

    logger.info("Done")
