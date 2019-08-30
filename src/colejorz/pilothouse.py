"""Pilothouse's module."""
import platform
import sys
from queue import Queue  # pylint: disable=unused-import
from time import sleep, time
from threading import Event, Thread
from typing import Dict, Union

from pkg_resources import parse_version

if parse_version('3.6') > parse_version(platform.python_version()):
    ModuleNotFoundError = ImportError  # pylint:disable=redefined-builtin
try:
    from RPi import GPIO
except ModuleNotFoundError:
    from unittest.mock import MagicMock

    GPIO = MagicMock()

FWD_PIN = 17
BCK_PIN = 18
PWM = 27
STBY_PIN = 23

MIN_SPEED = 50
MAX_SPEED = 100
SPEED_STEP = 10


class Pilothouse:  # pylint:disable=too-many-instance-attributes
    """
    Pilothouse class holding all the logic for analog trains.

    Properly sets forward and backward pins and also properly sets pwm pin
    to manage the speed.
    """

    FORWARD = 'forward'
    STOP = 'stop'
    BACKWARD = 'backward'

    def __init__(self, queue: "Queue[Union[int, Dict[str, int]]]") -> None:
        """Initialize pilothouse."""
        self.state = self.STOP
        self.pwm_value = 0
        self._init_gpio()
        self.report_status()

        self._queue = queue
        self.event = Event()
        self._stop = False
        self.thread = Thread(target=self.run_thread)
        self.thread.start()
        self._current_instruction_timed = 0

    def _init_gpio(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(STBY_PIN, GPIO.OUT)
        GPIO.setup(FWD_PIN, GPIO.OUT)
        GPIO.setup(BCK_PIN, GPIO.OUT)
        GPIO.setup(PWM, GPIO.OUT)
        GPIO.output(STBY_PIN, GPIO.HIGH)
        self.pwm = GPIO.PWM(PWM, 100)
        self.pwm.start(0)
        self.pwm_value = 0

    def run_thread(self) -> None:
        """Continuously monitor and apply speed change requests."""
        while not self._stop:
            self.event.wait()
            instruction = self._queue.get()
            self.change_speed(**instruction)  # type: ignore
            if self._queue.empty():
                # there is another instruction - start doing it
                self.event.clear()

    def change_speed(self, speed: int, timed: int = 0) -> None:
        """Change the state of the train."""
        if speed == 0:
            self.stop()
        elif speed < 0:
            # going backward
            if self.state == self.FORWARD:
                # changing the direction
                if not self.stop():
                    return
                sleep(1)
            self.state = self.BACKWARD
            GPIO.output(BCK_PIN, GPIO.HIGH)
            self.adjust_speed(abs(speed), timed)
        else:
            # going forward
            if self.state == self.BACKWARD:
                # changing the direction
                if not self.stop():
                    return
                sleep(1)
            self.state = self.FORWARD
            GPIO.output(FWD_PIN, GPIO.HIGH)
            self.adjust_speed(abs(speed), timed)

    def adjust_speed(self, level: int, timed: int = 0) -> bool:
        """
        Adjust train speed.

        :param int level: speed to aim to
        :param int timed: number of seconds to stop after
        :return: whether adjust has finished adjusting or not
        """
        self._current_instruction_timed = timed
        incr = 1
        if level == self.pwm_value and not timed:
            return True
        if level < self.pwm_value:
            incr = -1
        while level != self.pwm_value:
            if not self._queue.empty():
                # new instruction - stop doing this one, and exit
                return False
            self.pwm_value += incr
            # never go faster than 100%
            self.pwm_value = min(self.pwm_value, MAX_SPEED)
            self.pwm.ChangeDutyCycle(self.pwm_value)
            self.report_status()
            sleep(0.2)

        if timed:
            stop_at = time() + timed
            while stop_at > time():
                self._current_instruction_timed = int(stop_at - time())
                if not self._queue.empty():
                    # new instruction - stop doing this one, and exit
                    return True
                sleep(0.2)
            self.change_speed(0)
            return False
        return True

    def report_status(self) -> str:
        """Report current speed status to stdout."""
        if self.state == self.STOP:
            msg = 'Waiting at station!'
        else:
            msg = 'Going {direction} at {speed:02d}'.format(
                direction=self.state, speed=self.pwm_value
            )
        print(msg, end="\r")
        sys.stdout.flush()
        return msg

    def stop(self) -> bool:
        """
        Stop the train.

        :rtype: bool
        :returns: Whether the stop has been successful or not.
        """
        try:
            if self.adjust_speed(0):
                GPIO.output(BCK_PIN, GPIO.LOW)
                GPIO.output(FWD_PIN, GPIO.LOW)
                self.state = self.STOP
            else:
                return False
            return True
        finally:
            self.report_status()

    def exit(self) -> None:
        """Close pilothouse."""
        self._stop = True
        self._queue.put({'speed': 0, 'timed': 0})
        self.event.set()
        self.stop()
        self.pwm.stop()
        GPIO.cleanup()
        self.thread.join()

    @property
    def status(self) -> Dict['str', Union[int, str]]:
        """Return proper status data."""
        direction = {
            self.STOP: 0, self.FORWARD: 1, self.BACKWARD: -1
        }[self.state]
        run = 'Until next instruction received'
        if self._current_instruction_timed:
            run = 'Planning to run for {}'.format(
                self._current_instruction_timed
            )
        return {
            'speed': self.pwm_value * direction,
            'pilothouse': 'working' if self.thread.is_alive() else 'closed',
            'run': run,
        }
