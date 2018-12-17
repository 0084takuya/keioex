# coding:utf-8

import numpy as np
import cv2
import baserobot

class ScreenController(baserobot.Controller):
    def __init__(self, cmd_queue):
        super().__init__(cmd_queue)

    def handle_command(self):
        while True:
            cmd = self.cmd_queue.get()
            assert type(cmd) is np.ndarray, \
            'Screen:キューにはnumpy.ndarray型の変数を入れてください'
            
            cv2.imshow('Mumeikaneshige', cmd)
            cv2.waitKey(100)

