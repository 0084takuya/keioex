# coding:utf-8
import wiringpi as w
import time
import struct
import threading

import baserobot

MOTOR_RIGHT_CHANNEL = 1
MOTOR_LEFT_CHANNEL = 0
FREQUENCY = int(1e6)

class MotorController2(baserobot.Controller):
    def __init__(self, cmd_queue):
        super().__init__(cmd_queue)
        # チャネル番号をメンバとして持っておく
        self.right_channel = MOTOR_RIGHT_CHANNEL
        self.left_channel = MOTOR_LEFT_CHANNEL
        # 左右のモータを初期化する
        L6470_init(self.right_channel)
        L6470_init(self.left_channel)

        # 左右のモータの現在の速さを記憶しておく
        self._v_right = 0
        self._v_left = 0
        
        # 一度にあげることのできる最大速度
        # self.v_step = int(1e3)

        # 速度を変えることのできる最小時間間隔
        self.step_interval = 0.1
    
    def __del__(self):
        # 終了時はモーターを止める
        L6470_run(MOTOR_RIGHT_CHANNEL, 0)
        L6470_run(MOTOR_LEFT_CHANNEL, 1)
        print('MOTOR: STOP')

    def handle_command(self):
       # この関数は別プロセスで実行される
        while True:
            # 左右のタイヤの速度をキューで受け取る
            cmd = self.cmd_queue.get()
            
            # cmdの要素の数は2または3である
            assert len(cmd) == 2 or len(cmd) == 3, 'コマンドのフォーマットが違います'
            
            if len(cmd) == 2:
                v_right, v_left = cmd
                v_step = 1000
            else:
                v_right, v_left, v_step = cmd
            
            # intまたはfloatでない型が入力されたらassertを出す
            assert type(v_right) is int or type(v_right) is float,\
            'モータの速度は数値で入力してください'
            
            assert type(v_left) is int or type(v_left) is float,\
            'モータの速度は数値で入力してください'

            assert type(v_step) is int or type(v_step) is float,\
            'モータの加速度は数値で入力してください'

            if type(v_right) is float:
                v_right = int(v_right)
                print('float 型が入力されましたが, int型にキャストします')

            if type(v_left) is float:
                v_left = int(v_left)
                print('float 型が入力されましたが, int型にキャストします')

            if type(v_step) is float:
                v_step = int(v_step)
                print('float 型が入力されましたが, int型にキャストします')


            # -3e4 < v_right,v_left < 3e4の範囲でない速度が入力された場合
            if not -3e4 <= v_right <= 3e4:
                print('v_rightに範囲外の速度が入力されました')
                v_right = min(v_right, int(3e4))
                v_right = max(v_right, int(-3e4))

            if not -3e4 <= v_left <= 3e4:
                print('v_leftに範囲外の速度が入力されました')
                v_left = min(v_left, int(3e4))
                v_left = max(v_left, int(-3e4))

            if not 0 < v_step <= 3e4:
                print('v_stepに範囲外の速度が入力されました')
                v_step = min(v_step, int(3e4))
                v_step = max(v_step, 1)

            # 指定した速度にする
            self.set_v(v_right, v_left, v_step)
    
    def set_v(self, v_right, v_left, v_step):
        # 現在の速度と指定した速度の差
        dv_right = v_right - self._v_right
        dv_left = v_left - self._v_left
        # 加速する
        self.accelerate(dv_right, dv_left, v_step)

    def accelerate(self, dv_right, dv_left, v_step):
        # 左右のモータを別のスレッドで実行する
        t_right = threading.Thread(target = self._accelerate_right, args=(dv_right, v_step))
        t_left = threading.Thread(target = self._accelerate_left, args=(dv_left, v_step))
        t_right.start()
        t_left.start()

        t_right.join()
        t_left.join()

    def _accelerate_right(self, dv, v_step = 1000):
        # dv は加速する分の値
        # 型チェック
        assert type(dv) is int, '型が違います'
        # 加速度の方向
        direction = 1 if dv >= 0 else -1

        # ステップ数
        step = int(abs(dv) / v_step)

        for i in range(step):
            self._v_right += direction * v_step

            L6470_run(self.right_channel, int(-1 * self._v_right))

            time.sleep(self.step_interval)

    def _accelerate_left(self, dv, v_step = 1000):
        # dv 加速する分
        # 型チェック
        assert type(dv) is int, '型が違います'
        # 加速度の方向
        direction = 1 if dv >= 0 else -1

        # ステップ数
        step = int(abs(dv) / v_step)

        for i in range(step):
            self._v_left += direction * v_step

            L6470_run(self.left_channel, int(self._v_left))

            time.sleep(self.step_interval)

def L6470_write(channel, data):
    data = data.to_bytes(1, byteorder="big")

    w.wiringPiSPIDataRW(channel, data)
    #w.wiringPiSPIDataRW(channel, struct.pack("B", data))

def L6470_init(channel):
    w.wiringPiSPISetup(channel, FREQUENCY)
    #MAX_SPEEDの設定
    #レジスタアドレス
    L6470_write(channel, 0x07)
    #最大回転スピード値
    L6470_write(channel, 0x00)
    L6470_write(channel, 0x25)

    #KVAL_HOLDの設定
    #レジスタアドレス
    L6470_write(channel, 0x09)
    #モータ停止中の電圧の設定
    L6470_write(channel, 0xFF)

    #KVAL_RUN設定
    #レジスタアドレス
    L6470_write(channel, 0x0A)
    #モータ定速回転中の電圧設定
    L6470_write(channel, 0xFF)

    #KVAL_ACC設定
    #レジスタアドレス
    L6470_write(channel, 0x0B)
    #モータ加速中の電圧の設定
    L6470_write(channel, 0xFF)

    #KVAL_DECの設定
    #レジスタアドレス
    L6470_write(channel, 0x0C)
    #モータ減速中の電圧設定
    L6470_write(channel, 0x40)

    #OCD_TH設定
    #レジスタアドレス
    L6470_write(channel, 0x13)
    #オーバーカレントスレッショルド設定
    L6470_write(channel, 0x0F)

    #STALL_TH設定
    #レジスタアドレス
    L6470_write(channel, 0x14)
    #ストール電流スレッショルド設定
    L6470_write(channel, 0x7F)

    # start slopeデフォルト
    #レジスタアドレス
    L6470_write(channel, 0x0E)
    L6470_write(channel, 0x00)

    #デセラレーション設定
    #レジスタアドレス
    L6470_write(channel, 0x10)
    L6470_write(channel, 0x29)

def L6470_run(channel, speed):
    #方向検出
    direction = 0x50 if speed < 0 else 0x51
    speed = abs(speed)
    
    #コマンド送信
    L6470_write(channel, direction)
    #データ送信
    L6470_write(channel, (0x0F0000 & speed) >> 16)
    L6470_write(channel, (0x00FF00 & speed) >> 8)
    L6470_write(channel, (0x0000FF & speed))
    
def L6470_softstop(channel):
    direction = 0xB0
    #コマンド送信
    L6470_write(channel, direction)
    #time.sleep(1)

def main():
    pass
if __name__ == '__main__':
    main()
