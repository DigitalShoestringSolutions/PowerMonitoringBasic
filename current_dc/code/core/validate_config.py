import argparse
import tomli
import ipaddress
import logging
import re

logger = logging.getLogger(__name__)


def validate(config):
    logger.info("Beginning Validation")
    mqtt_config = config.get('mqtt')
    mqtt_valid = False
    if mqtt_config:
        mqtt_valid = validate_mqtt(mqtt_config)
        if mqtt_valid:
            logger.info("MQTT Config: VALID")
    else:
        logger.error("MQTT Config: INVALID - not found! Expected to be under tag 'mqtt'.")

    validate_measurement(config)

    pass


def validate_mqtt(mqtt_config):
    broker = mqtt_config.get('broker')
    broker_valid = False
    if broker is None:
        logger.error(f'MQTT Broker not specified, expected at mqtt.broker')
    else:
        try:
            ipaddress.ip_address(broker)
            logger.debug(f'MQTT Broker "{broker}" is a valid IP Address')
            broker_valid = True
        except:
            pattern = re.compile(r"^\w*(\.\w*)+$")
            if pattern.match(broker):
                broker_valid = True
                logger.warning(
                    f'CHECK: MQTT Broker "{broker}" is not a valid IP Address, but seems to be a valid DNS name.')
            else:
                logger.error(
                    f'MQTT Broker "{broker}" is not a valid IP Address, and does not seem to be a valid DNS name')

    port = mqtt_config.get('port')
    port_valid = False
    if port is None:
        logger.error(f'MQTT Port not specified, expected at mqtt.port')
    else:
        try:
            port_int = int(port)
            port_valid = True
            if port_int == 1883 or port_int == 8883:
                logger.debug(f'MQTT Port "{port}" is valid')
            else:
                logger.warning(
                    f'CHECK: MQTT Port "{port}" is valid, but not a typical value - 1883 and 8883 are commonly used.')
        except:
            logger.error(f'MQTT Port "{port}" is not a valid - must be a number - 1883 and 8883 are commonly used.')

    return broker_valid and port_valid


def validate_measurement(config):
    measurement_conf = config.get('measurement')
    if measurement_conf is None:
        logger.error("Measurement Config: INVALID - not found! Expected to be under tag 'measurement'.")
        return False

    pipelines_conf = config.get('pipelines')
    if pipelines_conf is None:
        logger.error(
            "Pipelines Config: INVALID - measurement has no sensing stacks! Expected to be under tag 'measurement.sensing_stacks'.")
        return False

    stacks = measurement_conf.get('sensing_stacks')
    if stacks is None:
        logger.error(
            "Measurement Config: INVALID - measurement has no sensing stacks! Expected to be under tag 'measurement.sensing_stacks'.")
        return False

    unique_stack_pipelines = []
    for stack in stacks:
        pipeline = stack.get('pipeline')
        if pipeline is None:
            logger.error(f"Sensing stack {stack} does not have a 'pipeline' specified")
            return False
        else:
            if pipeline not in unique_stack_pipelines:
                unique_stack_pipelines.append(pipeline)



#     for pipeline_name in unique_stack_pipelines:
#         # valid, output = validate_pipeline(pipeline_name,pipelines_conf,config)
#
# def validate_pipeline(pipeline_name,pipelines_conf,config):
#     spec = pipelines_conf.get(pipeline_name)


def get_config(filename='./config.toml'):
    try:
        with open(filename, "rb") as f:
            toml_conf = tomli.load(f)
        logger.debug(f"Raw Config: {toml_conf}")
        return toml_conf
    except FileNotFoundError:
        logger.error(f'Config file not found at "{filename}"')


if __name__ == "__main__":
    levels = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}
    parser = argparse.ArgumentParser(description='Validate config file for sensing data collection service module.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--log", choices=['debug', 'info', 'warning', 'error'], help="Log level", default='info',
                        type=str)
    parser.add_argument("--file", help="Config file to validate", default='./config.toml', type=str)
    args = parser.parse_args()

    logging.basicConfig(level=levels.get(args.log, logging.INFO),
                        format='%(levelname)-8s : %(message)s')
    conf = get_config(args.file)
    validate(conf)
