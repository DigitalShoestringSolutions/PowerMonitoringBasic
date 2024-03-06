import paho.mqtt.client as mqtt
import multiprocessing
import logging
import zmq
import json
import chevron
import time
import signal
from urllib.parse import urljoin

context = zmq.Context()
logger = logging.getLogger("main.mqtt_out")

terminate_flag = False

def graceful_signal_handler(sig, _frame):
    logger.info(f'Received {signal.Signals(sig).name}. Triggering graceful termination.')
    global terminate_flag
    terminate_flag = True
    signal.alarm(10)

class MQTTServiceWrapper(multiprocessing.Process):
    def __init__(self, config, zmq_conf):
        super().__init__()

        mqtt_conf = config['mqtt']
        self.url = mqtt_conf['broker']
        self.port = int(mqtt_conf['port'])

        self.topic_base = mqtt_conf.get('base_topic_template',"")

        self.initial = mqtt_conf['reconnect'].get('initial',5)
        self.backoff = mqtt_conf['reconnect'].get('backoff',2)
        self.limit = mqtt_conf['reconnect'].get('limit',60)

        # declarations
        self.zmq_conf = zmq_conf
        self.zmq_in = None

    def do_connect(self):
        self.zmq_in = context.socket(self.zmq_conf['type'])
        if self.zmq_conf["bind"]:
            self.zmq_in.bind(self.zmq_conf["address"])
        else:
            self.zmq_in.connect(self.zmq_conf["address"])

    def mqtt_connect(self, client, first_time=False):
        timeout = self.initial
        exceptions = True
        while exceptions and terminate_flag is False:
            try:
                if first_time:
                    client.connect(self.url, self.port, 60)
                else:
                    logger.error("Attempting to reconnect...")
                    client.reconnect()
                logger.info("Connected!")
                time.sleep(self.initial)  # to give things time to settle
                exceptions = False
            except Exception:
                logger.error(f"Unable to connect, retrying in {timeout} seconds")
                time.sleep(timeout)
                if timeout < self.limit:
                    timeout = timeout * self.backoff
                else:
                    timeout = self.limit

    def on_disconnect(self, client, _userdata, rc):
        if rc != 0:
            logger.error(f"Unexpected MQTT disconnection (rc:{rc}), reconnecting...")
            self.mqtt_connect(client)

    def run(self):
        signal.signal(signal.SIGINT, graceful_signal_handler)
        signal.signal(signal.SIGTERM, graceful_signal_handler)
        self.do_connect()

        client = mqtt.Client()
        # client.on_connect = self.on_connect
        # client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect

        # self.client.tls_set('ca.cert.pem',tls_version=2)
        logger.info(f'connecting to {self.url}:{self.port}')
        self.mqtt_connect(client, True)


        while terminate_flag is False:
            while self.zmq_in.poll(50, zmq.POLLIN):
                try:
                    msg = self.zmq_in.recv(zmq.NOBLOCK)
                    msg_json = json.loads(msg)
                    msg_path = msg_json['path']
                    msg_payload = msg_json['payload']
                    topic = chevron.render(urljoin(self.topic_base, msg_path), msg_payload)
                    logger.info(f'pub topic:{topic} msg:{msg_payload}')
                    client.publish(topic, json.dumps(msg_payload))
                except zmq.ZMQError:
                    pass
            client.loop(0.05)
        logger.info("Done")
