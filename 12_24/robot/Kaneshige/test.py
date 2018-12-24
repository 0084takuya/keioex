# coding: utf-8

import sys
sys.path.append('../')
import numpy as np
import cv2
import time

import mumeikaneshige as mk
from detect_human import main_process as human_detect

rage_word = ['馬鹿', 'マヌケ', 'アホ']
class Terminator(mk.Mumeikaneshige):
    def __init__(self):
        super().__init__()

    def get_rotate_angle(image, rocs, gakaku = 60):
        roc = rocs[0]
        center = int(image.shape[1]/2)
        # 右を正とする
        return (roc - center) / gakaku

    def go_time(speed=10000, t=1):
        self.controllers['Motor'].cmd_queue.put((speed, speed))
        time.sleep(t)    
        self.controllers['Motor'].cmd_queue.put((0, 0))

    def go_dist(speed=10000, d=2):
        t = d / 2
        self.controllers['Motor'].cmd_queue.put((speed, speed))
        time.sleep(t)    
        self.controllers['Motor'].cmd_queue.put((0, 0))
        
    def rotate_by_angle(angle):
        speed = angle
        self.controllers['Motor'].cmd_queue.put((5000,-5000))
        time.sleep(1)
        self.controllers['Motor'].cmd_queue.put((0, 0))
    
    def run(self):
        self.controllers['Motor'].cmd_queue.put((10000, -10000, 10000))
        time.sleep(3)
        self.controllers['Motor'].cmd_queue.put((0,0, 10000))
        
def main():
    robot = Terminator()
    robot.start()
    del robot
if __name__ == '__main__':
    main()
