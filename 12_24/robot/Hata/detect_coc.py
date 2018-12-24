#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import sys
argv = sys.argv
    
def calcCircleLevel (contour, area):
    perimeter = cv2.arcLength(contour, True)
    circle_level = 4.0 * np.pi * area / (perimeter * perimeter); # perimeter = 0 のとき気をつける
    return circle_level

def detect_coc(image):
    #image = cv2.resize(image, (int(image.shape[1]/2), int(image.shape[0]/2)))
    centers = []
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([80, 140, 0])
    upper = np.array([105, 255, 100])
    mask = cv2.inRange(image, lower, upper)
    image = cv2.bitwise_and(image, image, mask=mask)
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret,image = cv2.threshold(image,50,255,cv2.THRESH_TOZERO)
    kernel = np.ones((3,3), np.float32)/ 9
    image = cv2.dilate(image, kernel, iterations = 3)
    kernel_gauss = np.ones((3,3), np.float32)/9
    #image = cv2.filter2D(image, -1, kernel_gauss)
    #image = cv2.dilate(image, kernel_gauss, iterations = 3)
    #cv2.imwrite('data/mono.jpg', image)
    image, contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) >= 1:
        for cont in contours:
            (x,y),radius = cv2.minEnclosingCircle(cont)
            center = (int(x),int(y))
            radius = int(radius)
            if radius > 8 and radius < 20:
                image = cv2.circle(image,center,radius,(255,255,255),2)
                centers.append([int(x), int(y)])
                print(radius)
    # cv2.imwrite("data/result2.jpg", image)
    return centers
    
file_dir = 'data/'

def main_process(path):
    image = cv2.imread(path)
    return detect_coc(image)

if __name__ == '__main__':
    if len(argv) != 2:
        print("usage:python3 detect_coc.py file_name")
    else:
        print(main_process(argv[1]))  
