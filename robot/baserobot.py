#coding:utf-8

import multiprocessing as mp
import time

class BaseRobot:
    """
    overview: ロボットの抽象クラス
    """
    def __init__(self):
        self.senders = {}
        self.controllers = {}
    
    def __del__(self):
        pass

    def senders_start(self):
        """
        継承したクラスのrun()を実行する前にこの関数を実行してほしい
        """
        for key in self.senders.keys():
            self.senders[key].run()

    def controllers_start(self):
        """
        継承したクラスのrun()を実行する前にこの関数を実行してほしい
        """
        for key in self.controllers.keys():
            self.controllers[key].run()

    def run(self):
        assert False, '継承してください'
"""
    def start(self):
        p = mp.Process(target = self.run)
        p.start()
"""
    
class DataSender():
    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
    def __del__(self):
        pass

    def update(self):
        assert False, '継承してください'

    def run(self):
        p = mp.Process(target = self.update)
        p.start()

class Controller():
    def __init__(self, cmd_queue):
        self.cmd_queue = cmd_queue

    def handle_command(self):
        assert False, '継承してください'

    def run(self):
        p = mp.Process(target = self.handle_command)
        p.start()

def main():
    robot = RobotController()
    robot.run()

if __name__ == '__main__':
    main()
