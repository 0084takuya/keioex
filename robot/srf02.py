#coding:utf-8

import smbus
import pigpio
import time
import threading

import baserobot

class SRF02DataSender(baserobot.DataSender):
    def __init__(self, msg_queue):
        super().__init__(msg_queue)
        #0x71 front_right
        #0x70 front_left
        
        self.addr_list = [0x71, 0x73]

        # アドレスをキーとするbusのディクショナリ
        self.bus_dict = {self.addr_list[0]:smbus.SMBus(1), 
                         self.addr_list[1]:smbus.SMBus(1)}
        # アドレスをキーとするdistanceのディクショナリ
        self.distance_dict = {self.addr_list[0]:-1, 
                              self.addr_list[1]:-1}

    def measure_distance(self, address):
        # マルチスレッドで実行する関数
        try:
        
            # 測定開始命令
            self.bus_dict[address].write_byte_data(address, 0x00, 0x51)

            time.sleep(0.066) # 音波が飛んで反射して帰ってくるまでの時間
            # 測定結果の取り出し
            distance = \
                self.bus_dict[address].read_word_data(address, 0x02) >> 8
            # 測定結果を格納 5以下の数字が返ってきたら距離は1000とする
            self.distance_dict[address] = distance if distance > 5 else 1000
        except OSError:
            print('OSError')
            self.distance_dict[address] = 1000

    def update(self):
        thread_list = []
        while True:
            for addr in self.addr_list:
                t=threading.Thread(target = self.measure_distance, args=(addr,))
                thread_list.append(t)
            #測定を並列実行
            for t in thread_list:
                t.start()
            # 測定終了を待つ
            for t in thread_list:
                t.join()

            thread_list.clear()
            
            # キューで送るリストの作成
            keys_list = list(self.distance_dict.keys())
            distance_list = [] # msg_queueで送るリスト
            for key in keys_list:
                distance_list.append(self.distance_dict[key])
            
            # メッセージを送信
            while self.msg_queue.full(): 
                # このキューにputするのはこのプロセスしかないが
                # なんとなくwhile文を使う
                self.msg_queue.get() # 先頭の要素を捨てる
            self.msg_queue.put(distance_list, True) # 要素を追加
            
            time.sleep(0.1) # ちょっと待つ

