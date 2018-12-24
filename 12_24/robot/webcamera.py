# coding:utf-8

import cv2
import time

import baserobot

class WebcameraDataSender(baserobot.DataSender):
    def __init__(self, msg_queue, cam_right, cam_left):
        super().__init__(msg_queue)
        
        self.camera_right = cam_right
        self.camera_left = cam_left

        # self.frame_size = (240, 320)

    def __del__(self):
        pass

    def update(self):
        while True:
            # 撮影する
            _, frame_right = self.camera_right.read()
            _, frame_left = self.camera_left.read()

            # サイズを加工する
            # frame_right = cv2.resize(frame_right, self.frame_size)
            # frame_left = cv2.resize(frame_left, self.frame_size)
            
            # 満タンだったら先頭の要素を捨てる
            while self.msg_queue.full():
                self.msg_queue.get()
            
            # 左右で撮影した画像をそのまま出力
            self.msg_queue.put((frame_right, frame_left), True)

            time.sleep(0.25)


