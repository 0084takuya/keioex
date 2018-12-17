# coding:utf-8

import numpy as np
import cv2

import sys
sys.path.append('..')

import movidius

def main():
    path_to_graph = '../movidius/graph'
    categories = ('background','aeroplane', 'bicycle', 'bird', 'boat',
                  'bottle', 'bus', 'car', 'cat', 'chair','cow',
                  'diningtable', 'dog', 'horse','motorbike', 'person',
                  'pottedplant', 'sheep','sofa', 'train', 'tvmonitor')
    
    detector = movidius.MobileSSD(path_to_graph, categories)
    
    cam = cv2.VideoCapture(1)

    try:
        while True:
            _, frame = cam.read()
            if frame is None:
                print('Failed to take a picture')
                continue
            frame = cv2.resize(frame, (300, 300))
            result = detector.detect(frame)

            for item in result:
                if item['category'] != 'person':
                    continue

                cv2.rectangle(frame, (item['x1'], item['y1']), (item['x2'], item['y2']), (255,255,255), 2)

            cv2.imshow('test', frame)
            cv2.waitKey(100)

    finally:
        cam.release()
        

if __name__ == '__main__':
    main()
