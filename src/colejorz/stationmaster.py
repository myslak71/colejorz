import sys
from json import dumps
from time import sleep
from http.server import HTTPServer, BaseHTTPRequestHandler
from RPi import GPIO

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

    def speed_up(self):
        if self.pwm_value < MAX_SPEED:
            if self.pwm_value == 0:
                self.adjust_speed(MIN_SPEED)
            else:
                self.adjust_speed(self.pwm_value + SPEED_STEP)

    def slow_down(self):
        if self.pwm_value > MIN_SPEED:
            self.adjust_speed(self.pwm_value - SPEED_STEP)

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

    def forward(self):
        if self.state == self.FORWARD:
            return False
        self.stop()
        sleep(1)
        GPIO.output(FWD_PIN, GPIO.HIGH)
        self.state = self.FORWARD
        self.speed_up()

    def backward(self):
        if self.state == self.BACKWARD:
            return False
        self.stop()
        sleep(1)
        GPIO.output(BCK_PIN, GPIO.HIGH)
        self.state = self.BACKWARD
        self.speed_up()

    def report_status(self):
        if self.state == self.STOP:
            msg = 'Waiting at station!'
        else:
            msg = 'Going {direction} at {speed:02d}'.format(
                **self.state
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
    def train_state(self):
        return {
            'direction': self.state,
            'speed': self.pwm_value
        }


class StationDutyOffice(HTTPServer):

    def __init__(self, server_address, RequestHandlerClass):
        self.pilothouse = Pilothouse()
        super(StationDutyOffice, self).__init__(server_address, RequestHandlerClass)

    def server_close(self, *args, **kwargs):
        self.pilothouse.exit()
        print('Ostatnia stacja!\n')
        super(HTTPServer, self).server_close(*args, **kwargs)


class StationDutyRadio(BaseHTTPRequestHandler):
    
    def do_FWD(self):
        "Do get lost"
        self.server.pilothouse.forward()
        self.wfile.write('Triggering kolejka\n'.encode('utf-8'))

    def do_FASTER(self):
        "Faster."
        self.server.pilothouse.speed_up()
        self.wfile.write('Schneller! Speed at {}\n'.format(self.server.pilothouse.pwm_value).encode('utf-8'))

    def do_SLOWER(self):
        "Too fast!"
        self.server.pilothouse.slow_down()
        self.wfile.write('Too furious! Speed at {}\n'.format(self.server.pilothouse.pwm_value).encode('utf-8'))

    def do_BCK(self):
        "Do get lost"
        self.server.pilothouse.backward()
        self.wfile.write('We\'ve got to go back! Doc!\n'.encode('utf-8'))    

    def do_STOP(self):
        "I said STOP!"
        self.server.pilothouse.stop()
        self.wfile.write('Następna stacja, stop\n'.encode('utf-8'))    

    def do_TRAINWRECK(self):
        "I said STOP!"
        self.server.pilothouse.stop()
        self.wfile.write('This is a trainwreck! Let\'s revert!\n'.encode('utf-8'))

    def do_STATUS(self):
        "Provide current status"
        self.wfile.write((dumps(self.server.pilothouse.train_state)+'\n').encode('utf-8'))


def main():
    httpd = StationDutyOffice(('', 8000), StationDutyRadio)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    main()
