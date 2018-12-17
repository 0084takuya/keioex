# coding: utf-8

import sys
sys.path.append('../')
import numpy as np
import cv2
import time

import mumeikaneshige as mk
from detect_coc import detect_coc

class BugDestroyer(mk.Mumeikaneshige):
    def __init__(self):
        super().__init__()
        
        self.smash_point = [] # 画像の中の棒で叩ける座標

    def run(self):
        while True:
            # 画像を取得
            frame1, frame2 = self.senders['Webcamera'].msg_queue.get()
            
            # 画像の中から虫の座標を取得
            bug_point_list = detect_coc(frame1)

            if len(bug_point_list) > 0: # 虫がいないなら何もしない
                pass
                

def main():
    robot = BugDestroyer()
    robot.start()
    del robot
if __name__ == '__main__':
    main()
