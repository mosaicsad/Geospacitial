import cv2
import os
import numpy as np
import glob

data= glob.glob('/sample_drive/cam_1/'+"/*.jpg")
total_data_len = len(data)
img = cv2.imread('393408606.jpg')
sp = img.shape
sz1 = sp[0]  # height(rows) of image
sz2 = sp[1]  # width(colums) of image
sz3 = sp[2]  # the pixels value is made up of three primary colors
imgMagMean = np.zeros(img.shape[0:3], np.float)
progressBar = 0
lastProg = 0
#cv2.imwrite('testMean.bmp',imgMean)
for num in data:
    #str2 = '/Users/gaoyunfei/study/geospatial/sample_drive/cam_0/' + str(num) + '.jpg'
    image = cv2.imread(num)
    #b, g, r = cv2.split(image)
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)
    magImg = cv2.magnitude(sobelx, sobely)

    i = np.array(magImg, dtype=np.float)
    imgMagMean += i
    progress = ((progressBar) * 100) / total_data_len
    if progress >= lastProg:
        print ("Progress: " + str(progress) + "%")
        lastProg += 10
    progressBar += 1
imgMagMean /= total_data_len
#imgMagMean = 20 * imgMagMean
imgMean = np.array(np.round(imgMagMean),dtype=np.uint8)
cv2.imwrite('testimgMagMean1.bmp',imgMagMean)
cv2.namedWindow('showimage1', cv2.WINDOW_NORMAL)
cv2.imshow("Image",imgMean)
cv2.waitKey(0)
cv2.destroyALLWindows()
cv2.imshow(image)