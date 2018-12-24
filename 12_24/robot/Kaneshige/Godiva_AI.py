# coding: utf-8

import sys
sys.path.append('../')
import numpy as np
import cv2
import time
import mumeikaneshige as mk
from detect_human import main_process as human_detect
from human import main_process as h_detect

rage_word = ['馬鹿', 'マヌケ', 'アホ']
stop_word = ['ごめん', 'すみません']
apolo_word = ['ゆるして']
words = ['', '', '', '', '']
laugh = "uhuhu.wav"
okotta = "rage.wav"
mukka = "mukka.wav"
atack = "atack.wav"
hansei = "hansei.wav"
gomen = "gomen.wav"

class Terminator(mk.Mumeikaneshige):
    def __init__(self):
        super().__init__()

    def say(self, voice):
        self.controllers['JTalk'].cmd_queue.put(voice)

    def set_go(speed_right, speed_left, acc):
        self.controllers['Motor'].cmd_queue.put((speed_right, speed_left, acc))        

    def set_arm(angle):
        self.controllers['Arm'].cmd_queue.put(angle)
        
    def get_voice():
        return self.senders['Julius'].msg_queue.get()

    def get_sensor():
        return self.senders['SRF02'].msg_queue.get()

    def get_image():
        return self.senders['Webcamera'].msg_queue.get()

    def apologize(self):
      voice = self.get_voice()
      if voice in stop_word:
          self.say(gomen)
          return True
      else:
          self.say(mukka)
          return False

    def get_angle(self, image, roc, gakaku = 60):
        center = int(image.shape[1]/2)
        # 右を正とする
        return (roc - center) / gakaku

    def go_straight(self):
        speed = 30000
        self.set_go(speed, speed, speed)
        while True:
            dst_msg = self.get_sensor()
            print(dst_msg)
            if dst_msg[0] < 20 or dst_msg[1] < 20:
                self.set_go(0, 0, 30000)
                return True
   
    def rotate_by_angle(self, angle):
        speed = 10000
        t = angle/40*3 + 1/2
        self.set_go(speed, -speed, speed)
        time.sleep(t)
        self.set_go(0, 0, speed)
        
    def smash(self):
        self.set_arm(60)
        time.sleep(1)
        self.say(atack)
        self.set_arm(-30)
        time.sleep(1)
        self.set_arm(60)
       
        
    def rotate_six(self, right = True):
        speed =20000 if right else -20000
        self.set_go(speed, -speed, abs(speed))
        time.sleep(2)
        self.set_go(speed, -speed, abs(speed))
          
    def rage(self, rotate_rate = 60):
        find = False
        
        # start rage_mode
        print("Rage Mode...")
        self.smash()
        
        # search human to smash
        for i in range(int(360 / rotate_rate)):
            print("rotate to find human", i)
            self.rotate_six(right = True)
            print("stop and find human")
            frame1, frame2 = self.get_image()
            roc1 = h_detect(frame1)
            roc2 = h_detect(frame2)
            # if apologized finish
            if self.apologize():
                break
            
            # if found human
            if roc2 != 0:
                print("I found human!")
                print("tuple", roc2)
                self.say(okotta)
                print("adjust angle to smash")
                self.rotate_by_angle(self.get_angle(frame2, roc2))
                find = True
                break
            elif roc1 != 0:
                print("I found human!!!")
                print("tuple", roc1)
                self.say(okotta)
                print("adjust angle to smash")
                self.rotate_by_angle(self.get_angle(frame1, roc1))
                find = True
                break
            
            # if not found
            else:
                print("I couldn't find human...")
                self.say(mukka)
        
        # found! let's smash human!
        print("let's smash human")
        if find:
            if self.go_straight():
                self.smash()
                
                # everything is over, apologize
                time.sleep(2)
                self.say(gomen)
            find = False
        
        # couldn't find, akirame...        
        else:
            self.say(hansei)
        print("Rage mode finished...")
            
    def run(self): 
        print("Godiva_AI start running!!!")
        while True:
            voice = self.get_voice()
            if voice in rage_word:
                self.rage()
            else:
                self.say(laugh)
                
def main():
    robot = Terminator()
    robot.start()
    del robot
if __name__ == '__main__':
    main()
