# coding:utf-8

import time
import threading
import multiprocessing as mp
import queue
import sys
from datetime import datetime, timedelta
import sched
sys.path.append('../')
import cv2

import mumeikaneshige as mk
import movidius


class SampleRobot(mk.Mumeikaneshige):
    """
    中間発表で見せた挙動をするロボット
    """
    def __init__(self):
        # 親クラスのコンストラクタは最初に必ず明示的に呼ぶ
        super().__init__()

        # キーボード入力のスレッドの生成
        self.key_queue = mp.Queue()
        self.th_key_input = threading.Thread(target = self.key_input,
                              args = (self.key_queue,))

        self.th_key_input.start() # スレッドをスタートする

        # self.controllers['Arm'].cmd_queue.put(-20)

        # 画像の中の棒で叩ける四角形の座標[(x1, y1), (x2, y2)]
        self.smash_point = [(290, 330), (400, 350)]

        # movidius召喚
        path_to_graph = '../movidius/graph'
        categories = ('background','aeroplane', 'bicycle', 'bird', 'boat',
                      'bottle', 'bus', 'car', 'cat', 'chair','cow',
                      'diningtable', 'dog', 'horse','motorbike', 'person',
                      'pottedplant', 'sheep','sofa', 'train', 'tvmonitor')

        self.ssd_detector = movidius.MobileSSD('../movidius/graph', categories)

    def key_input(self, key_queue):
        while True:
            keys = input() # 入力を受け取る
            key_queue.put(keys, True) # 受け取ったら即キューに送信
    

    def run(self):
        # 実際の動作をここに書く

        #def def1(name):
        #    print(name)


        #now = datetime.now()
        #now = datetime(now.year, now.month, now.day, now.hour, 29, 0)
        #comp = datetime(now.year, now.month, now.day, now.hour, 29, 3)
        #diff = comp - now
        #print(diff)

        #if int(diff.days) >= 0:
        #    scheduler = sched.scheduler(time.time, time.sleep)
        #    scheduler.enter(diff.seconds, 1, def1, ("hoge", ))
        #    scheduler.run()
        #    self.controllers['Arm'].cmd_queue.put(50)
        #    time.sleep(1)
        #    self.controllers['Arm'].cmd_queue.put(-20)
        #else:
        #    print("do nothing")

        while True:
            # Webカメラの画像を取得
            frame1, frame2 = self.senders['Webcamera'].msg_queue.get()
            # Movidiusで演算
            
            result = self.ssd_detector.detect(cv2.resize(frame2, (300,300)))
            # 人の座標
            person_rect = None
            for item in result:
                if item['category'] == 'person':
                    person_pos = ((item['x1'], item['y1']), (item['x2'], item['y2']))
                    print(person_pos)
                    person_rect = person_pos
                    self.command()
                    break

            # 人が画像内にいない場合
            if person_rect is None:
                print ("none")
        # if 知っている人か
                # wav ”＠＠さんこんにちは、何分お休みになりますか？”
                # while 入力待ちjuliusからの文字列”＊＊分”
                    # "**分で記録して”おやすみなさい” カウントダウンして待つ"

            #else 知らない人か
                # wav "誰ですか名前を登録します"

    def command(self):
        print("command")
        while True:
            # キーボードのキューの確認
            try:
                keys = None # 何かしら入れておく特に大きな意味はない

                # 0.1秒経過してもキューが空だったらmp.Empty例外が出る
                keys = self.key_queue.get(timeout = 0.1)

                if 's' in keys or 'S' in keys: #ストップ
                    self.controllers['Motor'].cmd_queue.put((0,0))
                elif 'g' in keys or 'G' in keys:
                    self.controllers['Motor'].cmd_queue.put((10000, 10000))
                elif 'r' in keys or 'R' in keys:
                    self.controllers['Motor'].cmd_queue.put((-5000, 5000))
                elif 'l' in keys or 'L' in keys:
                    self.controllers['Motor'].cmd_queue.put((5000, -5000))
                elif 'b' in keys or 'B' in keys:
                    self.controllers['Motor'].cmd_queue.put((-10000,-10000))
                elif 'a' in keys or 'A' in keys:
                    self.controllers['Arm'].cmd_queue.put(50)
                    time.sleep(1)
                    self.controllers['Arm'].cmd_queue.put(-20)
                elif 'e' in keys or 'E' in keys:
                    self.controllers['Motor'].cmd_queue.put((e,e))
                else:
                    pass
            except queue.Empty:
                pass

            # Juliusから送られる文字列の確認
            try:
                julius_msg = None
                julius_msg = self.senders['Julius'].msg_queue.get(timeout = 0.1)
                if '止まれ' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((0,0))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '進め' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((10000,10000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '右' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((-5000, 5000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '左' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((5000, -5000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif '下がれ' in julius_msg:
                    self.controllers['Motor'].cmd_queue.put((-10000,-10000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
                elif 'やれ' in julius_msg:
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/test.wav')
                    self.controllers['Arm'].cmd_queue.put(50)
                    time.sleep(1)
                    self.controllers['Arm'].cmd_queue.put(-20)
                elif '５分' in julius_msg:
                    self.controllers['JTalk'].cmd_queue.put('/home/ri/work/robot/voice-sample/yes.wav')
                    print('5hun')
                else :
                    pass
            except queue.Empty:
                pass

def main():
    robot = SampleRobot()

    robot.run()
    del robot

if __name__ == '__main__':
    main()
