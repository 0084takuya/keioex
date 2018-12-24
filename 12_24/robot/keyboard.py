# coding:utf-8

import baserobot
import threading

class KeyboardDataSender(baserobot.DataSender):
    def __init__(self, msg_queue):
        super().__init__(msg_queue)

    def update(self):
        while True:
            keys = input()
            while self.msg_queue.full():
                self.msg_queue.get()
            self.msg_queue.put(keys, True)
"""
    def run(self):
        t = threading.Thread(target = self.update)
        t.start()
"""
