from time import sleep
from http.server import HTTPServer, BaseHTTPRequestHandler
from RPi import GPIO

FWD_PIN = 17
BCK_PIN = 18
PWM = 27


MIN_SPEED = 50
SPEED_STEP = 10

class Pilothouse:

    FORWARD = 'forward'
    STOP = 'stop'
    BACKWARD = 'backward'

    def __init__(self):
        self.state = self.STOP
        self.pwm_value = 0
        self._init_gpio()

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
        if self.pwm_value < 100:
            if self.pwm_value == 0:
                self.pwm_value = MIN_SPEED
            else:
                self.pwm_value += SPEED_STEP
            self.pwm_value = min(self.pwm_value, 100)
            self.pwm.ChangeDutyCycle(self.pwm_value)

    def slow_down(self):
        if self.pwm_value > MIN_SPEED:
            self.pwm_value -= SPEED_STEP
            self.pwm.ChangeDutyCycle(self.pwm_value)

    def forward(self):
        if self.state == self.FORWARD:
            return False
        self.stop()
        sleep(1)
        GPIO.output(FWD_PIN, GPIO.HIGH)
        self.speed_up()
        self.state = self.FORWARD

    def backward(self):
        if self.state == self.BACKWARD:
            return False
        self.stop()
        sleep(1)
        GPIO.output(BCK_PIN, GPIO.HIGH)
        self.speed_up()
        self.state = self.BACKWARD

    def stop(self):
        GPIO.output(BCK_PIN, GPIO.LOW)
        GPIO.output(FWD_PIN, GPIO.LOW)
        self.pwm_value = 0
        self.pwm.ChangeDutyCycle(self.pwm_value)
        self.state = self.STOP

    def exit(self):
        self.stop()
        self.pwm.stop()
        GPIO.cleanup()


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


def main():
    httpd = StationDutyOffice(('', 8000), StationDutyRadio)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    main()
