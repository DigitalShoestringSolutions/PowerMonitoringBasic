import traceback
import logging
import multiprocessing
import time
import datetime
import signal
import asyncio
import importlib
import core.pipeline
import core.sensing_stack
import core.output
import core.exceptions
import zmq

logger = logging.getLogger("main.measure")
context = zmq.Context()

terminate_flag = False


def setup_signal_handlers():
    signal.signal(signal.SIGINT, graceful_signal_handler)
    signal.signal(signal.SIGTERM, graceful_signal_handler)


def graceful_signal_handler(sig, _frame):
    logger.info(f'Received {signal.Signals(sig).name}. Triggering graceful termination.')
    global terminate_flag
    terminate_flag = True
    signal.alarm(10)


class BuildingBlockFramework(multiprocessing.Process):
    def __init__(self, config, zmq_conf):
        super().__init__()

        self.config = config
        self.name = config.get("service_module_name","sensing_dc")

        self.interface_config = config['interface']
        self.device_config = config['device']
        self.calculation_config = config['calculation']
        self.pipeline_config = config['pipelines']
        self.measurement_config = config['measurement']
        self.output_config = config['output']

        # declarations
        self.interfaces = {}
        self.devices = {}
        self.calculations = {}
        self.pipelines = {}
        self.sensing_stacks = []
        self.measurement_module = None

        self.zmq_conf = zmq_conf
        self.zmq_out = None

    def do_connect(self):
        self.zmq_out = context.socket(self.zmq_conf['type'])
        if self.zmq_conf["bind"]:
            self.zmq_out.bind(self.zmq_conf["address"])
        else:
            self.zmq_out.connect(self.zmq_conf["address"])

    def run(self):  # Execution Starts Here
        setup_signal_handlers()

        logger.info("+---Started")
        self.do_connect()
        # Load Elements
        logger.info("+---Loading Modules")
        self.load_modules()
        self.create_pipelines()
        self.create_sensing_stacks()

        asyncio.run(self.async_loop())

    # could be multiplexed as measurement loops
    async def async_loop(self):
        # Initialise Elements
        logger.info("+---Initialising Modules")
        await self.initialise_interfaces()
        self.initialise_devices()
        self.initialise_pipelines()
        self.initialise_sensing_stacks()
        self.initialise_measurement()

        logger.info("+---Starting Loop")
        while terminate_flag is False:
            try:
                delay, output_vars = await self.measurement_module.loop()

                if output_vars:
                    messages = self.generate_output(output_vars, self.output_config)
                    for message in messages:
                        self.dispatch(message)

                await asyncio.sleep(delay)
            except core.exceptions.SampleError as e:
                logger.error(f"Sample Error for device {e.device}: {e} - pausing for 30 seconds")
                self.dispatch_error('device',e.device,str(e))
                await asyncio.sleep(30)
            except core.exceptions.CalculationError as e:
                logger.error(f"Sample Error for device {e.module}: {e} - pausing for 30 seconds")
                self.dispatch_error('calculation',e.module,str(e))
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error during sampling: {traceback.format_exc()} - pausing for 30 seconds")
                await asyncio.sleep(30)

        logger.info("Done")

    def load_modules(self):
        # load general modules
        self.load_module_list(self.interfaces, 'core.interface_modules', self.interface_config, ['config'])
        self.load_module_list(self.devices, 'core.device_modules', self.device_config)
        self.load_module_list(self.calculations, 'core.calculation_modules', self.calculation_config)

        # load measurement
        self.measurement_module = self.load_single_module(
            'core.measurement_modules',
            self.measurement_config['module'],
            self.measurement_config['class'],
            {
                'config': self.measurement_config.get('config')
            })
        logger.debug(f"Loaded measurement: {self.measurement_module}")

    def load_module_list(self, output_dict, prefix, spec_dict, args=['config', 'variables']):
        for name, spec in spec_dict.items():
            output_dict[name] = self.load_single_module(
                prefix,
                spec['module'],
                spec['class'],
                {arg: spec.get(arg) for arg in args}
            )
        logger.debug(f"Loaded list: {output_dict}")

    def load_single_module(self, prefix, module_name, class_name, class_args):
        full_module_name = f"{prefix}.{module_name}"
        # get correct module
        try:
            module = importlib.import_module(full_module_name)
            logger.debug(f"Imported {full_module_name}")
        except ModuleNotFoundError:
            logger.error(f"Unable to import module {full_module_name}. Service Module may not function as intended")
            logger.error(traceback.format_exc())
            return

        # get class in module
        klass = getattr(module, class_name)
        obj = klass(**class_args)
        logger.info(f"Loaded: {full_module_name} > {class_name}")
        return obj

    def create_pipelines(self):
        self.pipelines = {name: core.pipeline.Pipeline(spec) for name, spec in self.pipeline_config.items()}

    def create_sensing_stacks(self):
        self.sensing_stacks = [core.sensing_stack.SensingStack(stack) for stack in
                               self.measurement_config['sensing_stacks']]

    async def initialise_interfaces(self):
        for _name, interface in self.interfaces.items():
            if interface is not None:
                result = interface.initialise()
                if asyncio.iscoroutine(result):
                    await result

    def initialise_devices(self):
        for dev_name, dev_spec in self.device_config.items():
            device = self.devices[dev_name]
            interface = self.interfaces[dev_spec['interface']]
            if device is not None:
                device.initialise(interface)

    def initialise_pipelines(self):
        for _name, pipeline in self.pipelines.items():
            if pipeline is not None:
                pipeline.initialise(self.calculations)

    def initialise_sensing_stacks(self):
        for stack in self.sensing_stacks:
            if stack is not None:
                stack.initialise(self.devices, self.pipelines)

    def initialise_measurement(self):
        self.measurement_module.initialise(self.sensing_stacks)

    def get_timestamp(self):
        __dt = -1 * (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)
        tz = datetime.timezone(datetime.timedelta(seconds=__dt))
        return datetime.datetime.now(tz=tz).isoformat()

    def generate_output(self, var_dict, output_config):
        dataset = {**var_dict}

        if "timestamp" not in dataset:
            dataset["timestamp"] = self.get_timestamp()

        outputs = []
        for _output_item, output_item_config in output_config.items():
            payload = core.output.generate_json_path_message(dataset, output_item_config['spec'])
            # payload = core.output.generate_basic_output(dataset,output_spec)
            outputs.append({'path': output_item_config.get('path', ""), 'payload': payload})

        return outputs

    def dispatch(self, output):
        logger.debug(f"dispatch to {output.get('path', '')} of {output['payload']}")
        self.zmq_out.send_json({'path': output.get('path', ""), 'payload': output['payload']})

    def dispatch_error(self,type,id,reason):
        payload = {
            'type': type,
            'id': id,
            'reason': reason,
            'timestamp': self.get_timestamp()
        }
        self.zmq_out.send_json({'path': f'/error/{self.name}', 'payload': payload})