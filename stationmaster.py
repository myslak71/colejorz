from time import sleep
from http.server import HTTPServer, SimpleHTTPRequestHandler
from RPi import GPIO

FWD_PIN = 17
BCK_PIN = 18
PWM = 27


def moove(fwd=False, bck=False, speed=1):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(FWD_PIN, GPIO.OUT)
    GPIO.setup(BCK_PIN, GPIO.OUT)
    GPIO.setup(PWM, GPIO.OUT)
    if fwd:
        GPIO.output(FWD_PIN, GPIO.LOW)
        GPIO.output(BCK_PIN, GPIO.LOW)
        sleep(1)
        GPIO.output(FWD_PIN, GPIO.HIGH)
        GPIO.output(PWM, GPIO.HIGH)
    elif bck:
        GPIO.output(FWD_PIN, GPIO.LOW)
        GPIO.output(BCK_PIN, GPIO.LOW)
        sleep(1)
        GPIO.output(BCK_PIN, GPIO.HIGH)
        GPIO.output(PWM, GPIO.HIGH)
    else:
        GPIO.output(BCK_PIN, GPIO.LOW)
        GPIO.output(FWD_PIN, GPIO.LOW)
        GPIO.output(PWM, GPIO.LOW)
        


class StationDutyOffice(HTTPServer):

    def server_close(self, *args, **kwargs):
        moove()
        print('Ostatnia stacja!\n')
        super(HTTPServer, self).server_close(*args, **kwargs)


class StationDutyRadio(SimpleHTTPRequestHandler):
    
    def do_FWD(self):
        "Do get lost"
        moove(fwd=True)
        self.wfile.write('Triggering kolejka\n'.encode('utf-8'))

    def do_BCK(self):
        "Do get lost"
        moove(bck=True)
        self.wfile.write('We\'ve got to go back! Doc!\n'.encode('utf-8'))    

    def do_STOP(self):
        "I said STOP!"
        moove()
        self.wfile.write('Następna stacja, stop\n'.encode('utf-8'))    

    def do_TRAINWRECK(self):
        "I said STOP!"
        moove()
        self.wfile.write('This is a trainwreck! Let\'s revert!\n'.encode('utf-8'))


def main():
    httpd = StationDutyOffice(('', 8000), StationDutyRadio)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    main()
