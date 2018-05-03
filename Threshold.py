import cv2
import os
import numpy as np
import glob
import matplotlib.pyplot as plt

image = cv2.imread('testimgMagMean3.bmp')
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
img = cv2.GaussianBlur(image,(3,3),0)
#imgThr = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C , cv2.THRESH_BINARY, 5, 10)
retval, im_at_fixed = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY)
cv2.namedWindow('result',cv2.WINDOW_NORMAL)
cv2.resizeWindow('result', 500,500)
cv2.imshow('result', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('imgThr3.bmp',im_at_fixed)