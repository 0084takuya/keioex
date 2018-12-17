# coding:utf-8

import multiprocessing as mp
import RPi.GPIO as GPIO
import wiringpi
import cv2

import baserobot
import arm
import julius
import motor
import jtalk
import srf02
import webcamera
import screen
import detect_stall
import keyboard

class Mumeikaneshige(baserobot.BaseRobot):
    def __init__(self):
        super().__init__()

        # デバイス達の初期設定
        wiringpi.wiringPiSetupGpio()
        self.cam_right = cv2.VideoCapture(16)
        self.cam_left = cv2.VideoCapture(17)

        # DataSenderの追加
        self.senders['Julius'] = julius.JuliusDataSender(mp.Queue(5))
        self.senders['SRF02'] = srf02.SRF02DataSender(mp.Queue(5))
        self.senders['Webcamera']= webcamera.WebcameraDataSender(mp.Queue(2), self.cam_right, self.cam_left)
        self.senders['DetectStall'] = detect_stall.DetectStallDataSender(mp.Queue(2))

        # Controllerの追加
        self.controllers['Arm'] = arm.ArmController2(mp.Queue())
        self.controllers['Motor'] = motor.MotorController2(mp.Queue())
        self.controllers['JTalk'] = jtalk.JTalkController(mp.Queue())
        self.controllers['Screen'] = screen.ScreenController(mp.Queue())
        
        # DataSender と Controller を起動する
        self.senders_start()
        self.controllers_start()
    
    def __del__(self):
        self.__cleanup()

    def __cleanup(self):
        # 終了時の処理
        GPIO.cleanup()
        self.cam_right.release()
        self.cam_left.release()
        print('Mumeikaneshige: cleanup()')

    def run(self):
        assert False, '継承してください'

    def start(self):
        # スタートで実行を開始する
        try:
            self.run()
        finally:
            pass

