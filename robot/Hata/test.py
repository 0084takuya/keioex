# coding: utf-8

import threading
import multiprocessing as mp
import time
import sys
sys.path.append('..')

import mumeikaneshige as mk


class Test(mk.Mumeikaneshige):
    def __init__(self):
        super().__init__()
        
        self.p_list = []
        
        self.p_list.append(mp.Process(target = self._sig_stall))

        for p in self.p_list:
            p.start()
        
    def run(self):
        print('Start')
        time.sleep(3)

        assert False

        return 
        while True:
            
            self.controllers['Arm'].cmd_queue.put(40)
            time.sleep(1)
            self.controllers['Arm'].cmd_queue.put(-40)
            time.sleep(1)

            
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

