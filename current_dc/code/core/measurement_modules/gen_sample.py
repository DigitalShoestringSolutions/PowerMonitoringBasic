import datetime
import time
import traceback
import logging
import statistics

logger = logging.getLogger(__name__)


class SingleSample:
    def __init__(self, config):
        self.period = config["period"]
        self.sensing_stack = None
        self.previous_timestamp = None

    def initialise(self, sensing_stacks):
        if len(sensing_stacks) == 1:
            self.sensing_stack = sensing_stacks[0]
        elif len(sensing_stacks) > 1:
            self.sensing_stack = sensing_stacks[0]
            logger.warning("Multiple sensing stacks provided - module expects 1 - using first")

    async def loop(self):
        var_dict = await self.sensing_stack.execute()

        return self.__optimise_delay(), var_dict

    def __optimise_delay(self):
        if self.previous_timestamp:
            delta = self.period - (time.monotonic() - self.previous_timestamp)
            self.delay = self.delay + 0.2 * delta
            logger.debug(f"delay: {delta}>>{self.delay}")
        else:
            self.delay = self.period

        if self.delay < 0:
            logger.warning("Negative delay - resetting to period")
            self.delay = self.period

        self.previous_timestamp = time.monotonic()
        return self.delay


class SingleSampleAvg:
    def __init__(self, config):
        self.full_period = config["period"]
        self.n_samples = config["n_samples"]
        self.current_sample = 0
        self.sensing_stack = None
        self.samples = []

        self.anchor_timestamp = None
        self.previous_target = None

    def initialise(self, sensing_stacks):
        if len(sensing_stacks) == 1:
            self.sensing_stack = sensing_stacks[0]
        elif len(sensing_stacks) > 1:
            self.sensing_stack = sensing_stacks[0]
            logger.warning("Multiple sensing stacks provided - module expects 1 - using first")

    async def loop(self):
        var_dict = await self.sensing_stack.execute()
        self.samples.append(var_dict)
        delay = self.__optimise_delay()

        self.current_sample += 1
        out = None
        if self.current_sample == self.n_samples:
            self.current_sample = 0
            out = self.__average_variables(self.samples)
            self.samples = []

        return delay, out

    def __optimise_delay(self):
        current_timestamp = time.monotonic()

        if self.anchor_timestamp is None or self.current_sample == 0:
            self.anchor_timestamp = current_timestamp

        next_target = ((self.current_sample + 1) / self.n_samples) * self.full_period + self.anchor_timestamp
        base_delay = next_target - current_timestamp

        if self.previous_target:
            delta = self.previous_target - current_timestamp
            self.delay_adjustment = self.delay_adjustment + 0.2 * delta
            # logger.debug(f"""anchor: {self.anchor_timestamp}, fraction: {((self.current_sample + 1) / self.n_samples)},
            # target:{next_target}, current:{current_timestamp}, p_target:{self.previous_target}, delta: {delta},
            # delay_adjustment: {self.delay_adjustment}, b_delay: {base_delay}, delay: {base_delay + self.delay_adjustment}""")

        else:
            self.delay_adjustment = 0


        if base_delay + self.delay_adjustment < 0:
            logger.warning("Negative delay - resetting adjustment")
            self.delay_adjustment = 0

        self.previous_target = next_target
        return base_delay + self.delay_adjustment

    def __average_variables(self, list):
        aggregated_dict = {}
        # aggregate
        for entry in list:
            for k, v in entry.items():
                if k not in aggregated_dict:
                    aggregated_dict[k] = []
                aggregated_dict[k].append(v)

        out = {}
        for k, v in aggregated_dict.items():
            try:
                mean = statistics.mean(v)
                out[k] = mean
            except TypeError:  # not numeric
                mode = statistics.mode(v)
                out[k] = mode

        return out


class MultiSampleMerged:
    def __init__(self, config):
        self.period = config["period"]
        self.sensing_stacks = None
        self.previous_timestamp = None

    def initialise(self, sensing_stacks):
        self.sensing_stacks = sensing_stacks

    async def loop(self):
        var_dict = {}
        for stack in self.sensing_stacks:
            res = await stack.execute()
            var_dict = {**var_dict, **res}
        return self.__optimise_delay(), var_dict

    def __optimise_delay(self):
        if self.previous_timestamp:
            delta = self.period - (time.monotonic() - self.previous_timestamp)
            self.delay = self.delay + 0.2 * delta
            logger.debug(f"delay: {delta}>>{self.delay}")
        else:
            self.delay = self.period


        if self.delay < 0:
            logger.warning("Negative delay - resetting to period")
            self.delay = self.period

        self.previous_timestamp = time.monotonic()
        return self.delay

class MultiSampleMergedAvg:
    def __init__(self, config):
        self.full_period = config["period"]
        self.n_samples = config["n_samples"]
        self.current_sample = 0
        self.sensing_stack = None
        self.samples = []


        self.anchor_timestamp = None
        self.previous_target = None


    def initialise(self, sensing_stacks):
        self.sensing_stacks = sensing_stacks

    async def loop(self):
        var_dict = {}
        for stack in self.sensing_stacks:
            res = await stack.execute()
            var_dict = {**var_dict, **res}

        self.samples.append(var_dict)
        delay = self.__optimise_delay()

        self.current_sample += 1
        out = None
        if self.current_sample == self.n_samples:
            self.current_sample = 0
            out = self.__average_variables(self.samples)
            self.samples = []

        return delay, out

    def __optimise_delay(self):
        current_timestamp = time.monotonic()

        if self.anchor_timestamp is None or self.current_sample == 0:
            self.anchor_timestamp = current_timestamp

        next_target = ((self.current_sample + 1) / self.n_samples) * self.full_period + self.anchor_timestamp
        base_delay = next_target - current_timestamp

        if self.previous_target:
            delta = self.previous_target - current_timestamp
            self.delay_adjustment = self.delay_adjustment + 0.2 * delta
            # logger.debug(f"""anchor: {self.anchor_timestamp}, fraction: {((self.current_sample + 1) / self.n_samples)},
            # target:{next_target}, current:{current_timestamp}, p_target:{self.previous_target}, delta: {delta},
            # delay_adjustment: {self.delay_adjustment}, b_delay: {base_delay}, delay: {base_delay + self.delay_adjustment}""")

        else:
            self.delay_adjustment = 0

        if base_delay + self.delay_adjustment < 0:
            logger.warning("Negative delay - resetting adjustment")
            self.delay_adjustment = 0

        self.previous_target = next_target
        return base_delay + self.delay_adjustment

    def __average_variables(self, list):
        aggregated_dict = {}
        # aggregate
        for entry in list:
            for k, v in entry.items():
                if k not in aggregated_dict:
                    aggregated_dict[k] = []
                aggregated_dict[k].append(v)

        out = {}
        for k, v in aggregated_dict.items():
            try:
                mean = statistics.mean(v)
                out[k] = mean
            except TypeError:  # not numeric
                mode = statistics.mode(v)
                out[k] = mode

        return out


class MultiSampleIndividual:
    def __init__(self, config):
        self.period = config["period"]
        self.sensing_stacks = None
        self.counter = 0
        self.previous_timestamp = None

    def initialise(self, sensing_stacks):
        self.sensing_stacks = sensing_stacks

    async def loop(self):
        stack = self.sensing_stacks[self.counter]
        var_dict = await stack.execute()

        self.counter = self.counter + 1
        if self.counter >= len(self.sensing_stacks):
            self.counter = 0

        delay = self.__optimise_delay() if self.counter == 0 else 0
        return delay, var_dict

    def __optimise_delay(self):
        if self.previous_timestamp:
            delta = self.period - (time.monotonic() - self.previous_timestamp)
            self.delay = self.delay + 0.2 * delta
            logger.debug(f"delay: {delta}>>{self.delay}")
        else:
            self.delay = self.period

        if self.delay < 0:
            logger.warning("Negative delay - resetting to period")
            self.delay = self.period

        self.previous_timestamp = time.monotonic()
        return self.delay


class MultiSampleIndividualAvg:
    def __init__(self, config):
        self.full_period = config["period"]
        self.n_samples = config["n_samples"]
        self.current_sample = 0
        self.sensing_stack = None
        self.samples = None

        self.stack_counter = 0
        self.anchor_timestamp = None
        self.previous_target = None

    def initialise(self, sensing_stacks):
        self.sensing_stacks = sensing_stacks
        self.samples = [[] for _i in range(len(self.sensing_stacks))]

    async def loop(self):
        stack = self.sensing_stacks[self.stack_counter]
        var_dict = await stack.execute()

        self.samples[self.stack_counter].append(var_dict)

        delay = 0
        out = None

        if self.current_sample == (self.n_samples - 1):
            logger.debug(f"sample:{self.current_sample},stack:{self.stack_counter}")
            out = self.__average_variables(self.samples[self.stack_counter])

        self.stack_counter = self.stack_counter + 1

        if self.stack_counter >= len(self.sensing_stacks):
            self.stack_counter = 0
            delay = self.__optimise_delay()
            self.current_sample += 1
            if self.current_sample == self.n_samples:
                self.current_sample = 0
                self.samples = [[] for _i in range(len(self.sensing_stacks))]

        return delay, out

    def __optimise_delay(self):
        current_timestamp = time.monotonic()

        if self.anchor_timestamp is None or self.current_sample == 0:
            self.anchor_timestamp = current_timestamp

        next_target = ((self.current_sample + 1) / self.n_samples) * self.full_period + self.anchor_timestamp
        base_delay = next_target - current_timestamp

        if self.previous_target:
            delta = self.previous_target - current_timestamp
            self.delay_adjustment = self.delay_adjustment + 0.2 * delta
            # logger.debug(f"""anchor: {self.anchor_timestamp}, fraction: {((self.current_sample + 1) / self.n_samples)},
            # target:{next_target}, current:{current_timestamp}, p_target:{self.previous_target}, delta: {delta},
            # delay_adjustment: {self.delay_adjustment}, b_delay: {base_delay}, delay: {base_delay + self.delay_adjustment}""")
        else:
            self.delay_adjustment = 0

        if base_delay + self.delay_adjustment < 0:
            logger.warning("Negative delay - resetting adjustment")
            self.delay_adjustment = 0

        self.previous_target = next_target
        return base_delay + self.delay_adjustment

    def __average_variables(self, list):
        aggregated_dict = {}
        # aggregate
        for entry in list:
            for k, v in entry.items():
                if k not in aggregated_dict:
                    aggregated_dict[k] = []
                aggregated_dict[k].append(v)

        out = {}
        for k, v in aggregated_dict.items():
            try:
                mean = statistics.mean(v)
                logger.debug(f"key: {k} - mean: {v} => {mean}")
                out[k] = mean
            except TypeError:  # not numeric
                mode = statistics.mode(v)
                out[k] = mode

        return out
