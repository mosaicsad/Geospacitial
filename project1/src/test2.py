# -*- coding: UTF-8 -*-
import cv2
import os
import numpy as np
import glob
import matplotlib.pyplot as plt



img = cv2.imread('393412611.jpg')
im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
im_at_mean = cv2.adaptiveThreshold(im_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 10)
retval, im_at_fixed = cv2.threshold(im_gray, 150, 255, cv2.THRESH_BINARY)
#cv2.imwrite('test.jpg', im_at_fixed)
img2 = cv2.imread('393412612.jpg')
im_gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
im_at_mean = cv2.adaptiveThreshold(im_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 10)
retval2, im_at_fixed2 = cv2.threshold(im_gray2, 150, 255, cv2.THRESH_BINARY)
#cv2.imwrite('test.jpg', im_at_fixed)
imgSub = np.zeros(im_gray.shape, np.float)
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        if(im_at_fixed[i, j] == im_at_fixed2[i, j]):
            imgSub[i,j] = 0
        else:
            imgSub[i,j] = 255

cv2.imwrite('imgSub2.bmp', imgSub)




