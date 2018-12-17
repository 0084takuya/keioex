# coding: utf-8

import wiringpi
import RPi.GPIO as GPIO
import time

import baserobot as br

class DetectStallDataSender(br.DataSender):
    def __init__(self, msg_queue):
        super().__init__(msg_queue)

        self._pin = 4

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN)

    def update(self):
        while True:
            while self.msg_queue.full():
                self.msg_queue.get()
            self.msg_queue.put(GPIO.input(self._pin), True)
            time.sleep(0.1)
