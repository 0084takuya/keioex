#coding:utf-8

import sys
import numpy as np
import cv2

def main():
    cap = cv2.VideoCapture(1)
    
    try:
        _, frame = cap.read()

        cv2.imwrite(sys.argv[1], frame)
    finally:
        cap.release()
    

if __name__ == '__main__':
    main()
