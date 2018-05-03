import cv2
import os
import numpy as np
import glob

data= glob.glob('/Users/gaoyunfei/study/geospatial/sample_drive/cam_3/'+"/*.jpg")
total_data_len = len(data)
img = cv2.imread('393408606.jpg')
sp = img.shape
sz1 = sp[0]  # height(rows) of image
sz2 = sp[1]  # width(colums) of image
sz3 = sp[2]  # the pixels value is made up of three primary colors
imgMean = np.zeros(img.shape, np.float)
progressBar = 0
lastProg = 0
#cv2.imwrite('testMean.bmp',imgMean)
for num in data:
    #str2 = '/Users/gaoyunfei/study/geospatial/sample_drive/cam_0/' + str(num) + '.jpg'
    image = cv2.imread(num)
    #b, g, r = cv2.split(image)
    i = np.array(image, dtype=np.float)
    imgMean += i
    progress = ((progressBar) * 100) / total_data_len
    if progress >= lastProg:
        print ("Progress: " + str(progress) + "%")
        lastProg += 10
    progressBar += 1
imgMean /= total_data_len
imgMean = np.array(np.round(imgMean),dtype=np.uint8)
cv2.imwrite('testMean3.bmp',imgMean)
cv2.namedWindow('showimage3', cv2.WINDOW_NORMAL)
cv2.imshow("Image",imgMean)
cv2.waitKey(0)
cv2.destroyALLWindows()
cv2.imshow(image)