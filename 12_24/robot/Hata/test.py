# coding: utf-8

import threading
import multiprocessing as mp
import time
import sys
sys.path.append('..')

import mumeikaneshige as mk
import movidius
from detect_coc import detect_coc


class Test(mk.Mumeikaneshige):
    def __init__(self):
        super().__init__()
        
        # グラフのバイナリファイルのパス
        path_to_graph = '../movidius/graph'
        # カテゴリのタプル 上記のグラフを用いるなら下記のカテゴリはコピペでよい
        categories = ('background','aeroplane', 'bicycle', 'bird', 'boat',
                  'bottle', 'bus', 'car', 'cat', 'chair','cow',
                  'diningtable', 'dog', 'horse','motorbike', 'person',
                  'pottedplant', 'sheep','sofa', 'train', 'tvmonitor')
        # self.detector = movidius.MobileSSD(path_to_graph, categories)
        
        

    def run(self):
        frame1, frame2 = self.senders['Webcamera'].msg_queue.get()
        while True:
            frame1, frame2 = self.senders['Webcamera'].msg_queue.get()
            if frame1 is None:
                continue

            coc_pos_list = detect_coc(frame2)
            print(coc_pos_list)
            
            if len (coc_pos_list) == 0:
                continue

            coc_pos = (coc_pos_list[0][0] - frame2.shape[1] / 2, coc_pos_list[0][1] - frame2.shape[0] / 2)

            print(coc_pos)

            
        

    def _sig_stall(self):
        while True:
            msg = self.senders['DetectStall'].msg_queue.get()
            print(msg)
            if msg > 0:
                self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')

if __name__ == '__main__':
    robot = Test()
    robot.run()
    del robot

