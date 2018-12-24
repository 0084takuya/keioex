#coding:utf-8

import sys
import numpy as np
import cv2
from time import sleep

def main():
    cap = cv2.VideoCapture(0)
    
    try:
        for i in range(100):
            _, frame = cap.read()
        
            cv2.imwrite(str(i) + '.jpg', frame)
            print("pic :",str(i))
            sleep(4)
    finally:
        cap.release()
    

if __name__ == '__main__':
    main()
