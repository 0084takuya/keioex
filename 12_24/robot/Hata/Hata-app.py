# coding: utf-8

import sys
sys.path.append('../')
import numpy as np
import cv2
import time
from queue import Empty

import mumeikaneshige as mk
from detect_coc import detect_coc
import movidius

class BugDestroyer(mk.Mumeikaneshige):
    def __init__(self):
        super().__init__()
        
        # 画像の中の棒で叩ける四角形の座標[(x1, y1), (x2, y2)]
        self.smash_point = [(290, 330), (400, 350)]
        
        # 何回連続してGを検出できなかったら見失ったとするか
        self.miss_coc_count_limit = 4 

        # movidius召喚
        path_to_graph = '../movidius/graph'
        categories = ('background','aeroplane', 'bicycle', 'bird', 'boat',
                      'bottle', 'bus', 'car', 'cat', 'chair','cow',
                      'diningtable', 'dog', 'horse','motorbike', 'person',
                      'pottedplant', 'sheep','sofa', 'train', 'tvmonitor')
    
        self.ssd_detector = movidius.MobileSSD('../movidius/graph', categories)
        
        # 状態の関数のディクショナリ
        self.state_func_dict = {}
        self.state_func_dict['start'] = self._state_func_start
        self.state_func_dict['where'] = self._state_func_where
        self.state_func_dict['control'] = self._state_func_control
        self.state_func_dict['chase_coc'] = self._state_func_chase_coc
        self.state_func_dict['smash_coc'] = self._state_func_smash_coc
        self.state_func_dict['extermed_coc'] = self._state_func_extermed_coc
        self.state_func_dict['chase_person'] = self._state_func_chase_person

    def run(self):
        print('READY')
        s = 'start'
        while True:
            s = self.trans_state(s)
    
    def trans_state(self, s):
        next_s = self.state_func_dict[s]()

        print(str(s) + ' --> ' + str(next_s))

        return next_s

    def _state_func_start(self):
        # EFFECTS : 初期状態
        while True:
            try:
                # 一旦キューを空にする
                while not self.senders['Julius'].msg_queue.empty():
                    self.senders['Julius'].msg_queue.get()
                # 空にしてから待つ
                msg = self.senders['Julius'].msg_queue.get(timeout = 0.1)
            
                if '虫でた' in msg:
                    # どこ？と言う状態に遷移
                    return 'where'

            except Empty:
                pass
            
            # Gがいるかどうか
            frame1, frame2 = self.senders['Webcamera'].msg_queue.get()
            coc_pos_list = detect_coc(frame1)
            if len(coc_pos_list) > 0:
                self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')
                return 'chase_coc'
            
    def _state_func_where(self):
        # EFFECTS : "どこ？"と言う
        self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')

        return 'control'
        
    def _state_func_control(self):
        # EFFECTS : 指示に従う状態
        while True:
            try:
                # 一旦キューを空にする
                while not self.senders['Julius'].msg_queue.empty():
                    self.senders['Julius'].msg_queue.get()
                # 空にしてから待つ
                msg = self.senders['Julius'].msg_queue.get(timeout = 0.1)
            
                if '右' in msg:
                    self.controllers['Motor'].cmd_queue.put((-5000, 5000))
                    self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')

                elif '左' in msg:
                    self.controllers['Motor'].cmd_queue.put((5000, -5000))
                    self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')
            
                elif '前' in msg:
                    self.controllers['Motor'].cmd_queue.put((10000, 10000))
                    self.controllers['JTalk'].cmd_queue.put('./voice-sample/yes.wav')
            
            except Empty:
                pass

            # ウェブカメラは常にあたらしい画像を送り続けているのでキューを空にする必要はない
            frame1, frame2 = self.senders['Webcamera'].msg_queue.get()
            # Gの検出
            coc_pos_list = detect_coc(frame1)
            print(coc_pos_list)
            
            if len(coc_pos_list) > 0:
                self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')
                return 'chase_coc'
    
    def _state_func_chase_coc(self):
        # EFFECTS : 虫を追跡する
        miss_count = 0 # 連続で見失った回数

        while True:
            frame1, frame2 = self.senders['Webcamera'].msg_queue.get()
            coc_pos_list = detect_coc(frame1)
            
            # 見失ったかどうかの処理
            if len(coc_pos_list) == 0:
                miss_count += 1 # インクリメント
                if miss_count >= self.miss_coc_count_limit:
                    self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')
                    return 'where'
            else:
                miss_count = 0
                # 虫が射程内にいるかどうか
                print(coc_pos_list)
                if self.smash_point[0][0] < coc_pos_list[0][0] < self.smash_point[1][0] and \
                    self.smash_point[0][1] < coc_pos_list[0][1] < self.smash_point[1][1]:
                    return 'smash_coc'
    
    def _state_func_smash_coc(self):
        # EFFECTS : 虫を叩く
        # 一旦止まる
        self.controllers['Motor'].cmd_queue.put((0,0))
        # 叩く
        self.controllers['Arm'].cmd_queue.put(-30)
        time.sleep(1)
        # 上げる
        self.controllers['Arm'].cmd_queue.put(60)
        # 一定時間待つ
        time.sleep(2)

        frame1, frame2 = self.senders['Webcamera'].msg_queue.get()

        # 虫が動いたかどうかの判定
        coc_pos_list = detect_coc(frame1)

        # 虫が画面にいない
        if len(coc_pos_list) == 0:
            # やれなかったと言う
            self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')
            return 'chase_coc'
        
        # 射程圏外にいる
        if not self.smash_point[0][0] < coc_pos_list[0][0] < self.smash_point[1][0] or \
           not self.smash_point[0][1] < coc_pos_list[0][1] < self.smash_point[1][1]:
            
            # やれなかったと言う
            self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')
            return 'chase_coc'

        # 射程圏内から動いていない
        self.controllers['JTalk'].cmd_queue.put('../voice-sample/yes.wav')
        return 'extermed_coc'

    def _state_func_extermed_coc(self):
        # EFFECTS : 虫を退治した状態
        while True:
            try:
                msg = self.senders['Julius'].msg_queue.get(timeout = 0.1)
                if 'お疲れ' in msg:
                    return 'start'
                elif 'やるじゃん' in msg:
                    return 'chase_person'
            except:
                pass

    def _state_func_chase_person(self):
        # EFFECTS : 人を追跡する
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
                    break
            
            # 人が画像内にいない場合
            if person_rect is None:
                return 'extermed_coc'
            
            # 人が射程圏内にいるなら
            # 人が画像内にいる場合は追跡
            
            

def main():
    robot = BugDestroyer()
    robot.start()
    del robot
if __name__ == '__main__':
    main()
