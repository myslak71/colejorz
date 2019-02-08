import sys
from json import dumps
from time import sleep
from http.server import HTTPServer, BaseHTTPRequestHandler
try:
    from RPi import GPIO
except ModuleNotFoundError:
    from unittest.mock import MagicMock
    GPIO = MagicMock()

FWD_PIN = 17
BCK_PIN = 18
PWM = 27


MIN_SPEED = 50
MAX_SPEED = 100
SPEED_STEP = 10

class Pilothouse:

    FORWARD = 'forward'
    STOP = 'stop'
    BACKWARD = 'backward'

    def __init__(self):
        self.state = self.STOP
        self.pwm_value = 0
        self._init_gpio()
        self.report_status()

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(FWD_PIN, GPIO.OUT)
        GPIO.setup(BCK_PIN, GPIO.OUT)
        GPIO.setup(PWM, GPIO.OUT)
        self.pwm = GPIO.PWM(PWM, 100)
        self.pwm.start(0)
        self.pwm_value = 0

    def change_speed(self, speed):
        """Change the state of the train."""
        if speed == 0:
            self.stop()
        elif speed < 0:
            # going backward
            if self.state == self.FORWARD:
                # changing the direction
                self.stop()
                sleep(1)
            self.state = self.BACKWARD
            GPIO.output(BCK_PIN, GPIO.HIGH)
            self.adjust_speed(abs(speed))
        else:
            # going forward
            if self.state == self.BACKWARD:
                # changing the direction
                self.stop()
                sleep(1)
            self.state = self.FORWARD
            GPIO.output(FWD_PIN, GPIO.HIGH)
            self.adjust_speed(abs(speed))

    def adjust_speed(self, level):
        incr = 1
        if level == self.pwm_value:
            return
        if level < self.pwm_value:
            incr = -1
        elif level > self.pwm_value:
            incr = 1
        while level != self.pwm_value:
            self.pwm_value += incr
            # never go faster than 100%
            self.pwm_value = min(self.pwm_value, MAX_SPEED)
            self.pwm.ChangeDutyCycle(self.pwm_value)
            self.report_status()
            sleep(0.2)

    def report_status(self):
        if self.state == self.STOP:
            msg = 'Waiting at station!'
        else:
            msg = 'Going {direction} at {speed:02d}'.format(
                direction=self.state, speed=self.pwm_value
            )
        print(msg, end="\r")
        sys.stdout.flush()

    def stop(self):
        self.adjust_speed(0)
        GPIO.output(BCK_PIN, GPIO.LOW)
        GPIO.output(FWD_PIN, GPIO.LOW)
        self.state = self.STOP
        self.report_status()

    def exit(self):
        self.stop()
        self.pwm.stop()
        GPIO.cleanup()

    @property
    def status(self):
        direction = {
            self.STOP: 0, self.FORWARD: 1, self.BACKWARD: -1
        }[self.state]
        return {
            'speed': self.pwm_value * direction
        }
