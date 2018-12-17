# coding:utf-8

import numpy as np
import cv2
import sys

def main():
    print(sys.argv[1])
    img = cv2.imread(sys.argv[1])
    cv2.imshow(sys.argv[1], img)

    cv2.waitKey(0)

if __name__ == '__main__':
    main()
