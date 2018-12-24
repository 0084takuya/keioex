# coding: utf-8
import sys
from mvnc import mvncapi as mvnc
import numpy as np
import cv2
import time

class MobileSSD():
    """
    MobileSSD検出器をMovidiusで簡単に動かすためのクラス
    Movidiusは1本しか刺さっていない前提である.
    """
    def __init__(self, path_to_graph, categories):
        assert type(path_to_graph) is str, '文字列を指定してください'
        assert type(categories) is tuple or type(categories) is list, 'タプルかリストを指定してください'
        
        # グラフファイルまでのパスをなんとなく保存しておく
        self.path_to_graph = path_to_graph
        # カテゴリのリストを受け取る
        self.categories = categories

        # おまじない
        mvnc.SetGlobalOption(mvnc.GlobalOption.LOG_LEVEL, 2)
        
        # Movidiusを読み込む
        devices = mvnc.EnumerateDevices()

        if len(devices) == 0: # 1本も見つからなかったら何もしない
            print('No devices found')
            return 
        
        # セットアップ
        self.device = mvnc.Device(devices[0])
        self.device.OpenDevice()

        # graphファイルを読み込む
        with open(self.path_to_graph, mode= 'rb') as f:
            graphfile = f.read()
        
        # デバイスにグラフファイルをセットする. 
        # self.graphオブジェクトを使って検出を行う
        self.graph = self.device.AllocateGraph(graphfile)

    def detect(self, img):
        """
        requires: imgは300x300の大きさのBGR画像ファイルである.
        effects : imgから検出された結果を返す.
            ディクショナリのフォーマットは
            'カテゴリ名':{'accuracy':, 'x':, 'y':, 'width':, 'height':}]
                  である.
        """
        # movidiusに画像を送信
        self.graph.LoadTensor(self.__preprocess_image(img), None)
        
        # movidiusでの演算結果を受けとる
        result, usrobj = self.graph.GetResult()

        # データを使いやすいように整形して返す.   
        return self.__convert_to_dict(result, img.shape)
    
    def __preprocess_image(self, img):
        """
        requires: imgは任意の大きさの画像ファイルである.
        effects : imgをMobileSSDで扱えるように変換する.
        """
        img = (cv2.resize(img, (300, 300)) - 127.5) * 0.007843
        
        return img.astype(np.float16)

    def __convert_to_dict(self, result, image_shape):
        """
        requires: resultはMobileSSDの結果のnp.ndarrayである.
        image_shapeは入力画像の形
        effects : MobileSSDの結果をディクショナリに変換する
        """
        assert type(result) == np.ndarray
        assert type(image_shape) == tuple
        ret = [] # 戻り値
        num_valid_boxes = int(result[0]) # 検出された四角形の数

        for idx_box in range(num_valid_boxes):
            # 一つの四角形ごとの結果の配列を抜き出す
            #result_box = result[7 + 7 * idx_box : 14 + 7 * idx_box]
            result_box = result[7 * (idx_box + 1) : 7 * (idx_box + 1) + 7]

            # どれか一つでも変な値が入っていたら変換不可なので次の四角形へ
            if np.isfinite(result_box).prod() == 0:
                continue

            # 戻り値のリストに追加
            ret.append({})
            ret[-1]['category'] = self.categories[int(result_box[1])] # カテゴリ名
            ret[-1]['accuracy'] = result_box[2]
            ret[-1]['x1'] = int(result_box[3] * image_shape[0])
            ret[-1]['y1'] = int(result_box[4] * image_shape[1])
            ret[-1]['x2'] = int(result_box[5] * image_shape[0])
            ret[-1]['y2'] = int(result_box[6] * image_shape[1])

        return ret

def main():
    import sys
    # グラフのバイナリファイルのパス
    path_to_graph = '../movidius/graph'
    # カテゴリのタプル 上記のグラフを用いるなら下記のカテゴリはコピペでよい
    categories = ('background','aeroplane', 'bicycle', 'bird', 'boat',
                  'bottle', 'bus', 'car', 'cat', 'chair','cow',
                  'diningtable', 'dog', 'horse','motorbike', 'person',
                  'pottedplant', 'sheep','sofa', 'train', 'tvmonitor')
    # 検出器の生成
    ssd = MobileSSD(path_to_graph, categories)
    
    # 画像の読み込みと(300, 300)に整形
    img = cv2.imread(sys.argv[1])
    img = cv2.resize(img, (300, 300))
    
    # 検出器に画像を入力して結果を取得
    result = ssd.detect(img)
    # 検出器の返す結果はディクショナリのリストになっている
    # ひとつの検出結果は
    # {'category':, 'accuracy':, 'x1':, 'x2':, 'y1':, 'y2':}
    # のディクショナリで表される.
    # ディクショナリの要素は
    # category: カテゴリの文字列
    # accuracy: 検出結果の正しい確率
    # x1: 検出した範囲の左上のx座標
    # x2: 検出した範囲の右下のx座標
    # y1: 検出した範囲の左上のy座標
    # y2: 検出した範囲の右下のy座標
    # となっている

    print(result)
    
    for item in result:
        cv2.rectangle(img, (item['x1'], item['y1']), (item['x2'], item['y2']), (255,255,255), 2)

    cv2.imshow('movidius test', img)
    cv2.waitKey(0)

if __name__ == '__main__':
    main()

