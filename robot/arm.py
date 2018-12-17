# coding:utf-8

import multiprocessing as mp
import time
import threading
import RPi.GPIO as GPIO
import wiringpi

import baserobot

class ArmController2(baserobot.Controller):
    def __init__(self, cmd_queue):
        super().__init__(cmd_queue)
        
        self.left_pin = 18
        self.right_pin = 19
        
        # mumeikaneshige クラスで初期化
        # wiringpi.wiringPiSetupGpio()

        wiringpi.pinMode(self.left_pin, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pinMode(self.right_pin, wiringpi.GPIO.PWM_OUTPUT)
        
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)

        wiringpi.pwmSetClock(375)
        wiringpi.pwmSetRange(1024)
        
    def handle_command(self):
        while True:
            angle = self.cmd_queue.get()
            print('Arm: ' + str(angle))

            if not -60 <= angle <= 60:
                print('Arm: -60度以上60度以下の範囲の角度を指定してください')
                angle = max(-60, angle)
                angle = min(60, angle)
            
            wiringpi.pwmWrite(self.left_pin, int((angle*0.05+7.5)*1024/100))
            wiringpi.pwmWrite(self.right_pin,int((-angle*0.05+7.5)*1024/100))
            
