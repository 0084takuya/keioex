# coding:utf-8

import socket

import baserobot

class JuliusDataSender(baserobot.DataSender):
    def __init__(self, msg_queue):
        super().__init__(msg_queue)
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def update(self):
        bufsize = 1024
        host = "localhost"
        port = 10500

        self.client.connect((host, port))
        while True:
            msg = self.client.recv(bufsize).decode('utf-8')

            if 'WORD=' in msg:
                word = self.__pick_word(msg)

                while self.msg_queue.full():
                    self.msg_queue.get()

                self.msg_queue.put(word, True)
    
    def __pick_word(self, msg):
        # requires: msg の中に'WORD='という文字列を必ず含む
        # effects : msg の中の単語を抽出する
        start_idx = 0
        end_idx = 0
        
        for i in range(len(msg)):
            if msg[i:i+5] == 'WORD=':
                start_idx = i + 6
                break
                
        for i in range(start_idx, len(msg)):
            if msg[i] == '"':
                end_idx = i
                break

        return msg[start_idx:end_idx]

        
            
