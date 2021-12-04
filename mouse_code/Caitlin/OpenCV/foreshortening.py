# Quantify foreshortening to determine distance to points
# width of tape: 0.75 in = 19.05 mm
# OpenCV camera calibration: https://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration/camera_calibration.html
# Paper on perspective distortion: https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8960275
# Plan: Tape width has direct relation to y axis pixel value.
#       Tape width also has direct relation to distance from camera.
#       Ultimately want relationship between y axis pixel value and distance from camera.

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
from PIL import Image
og_img = cv2.imread('cal2.jpg')

c = 0.3                                                     # crop factor
c_add = 0
c_h = 200
c_v = 150

img = og_img[int(len(og_img)*c)+c_add:len(og_img)-c_v, c_h:len(og_img[0])-c_h]
cv2.imshow('img',img)
cv2.waitKey(1)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,200,255)
print(edges.shape)
cv2.imwrite('edges.jpg',edges)

#lines = cv2.HoughLines(edges,1,np.pi/180,120)
lines = cv2.HoughLinesP(edges,1,np.pi/180,15,minLineLength=15,maxLineGap=5)

# for camera3.jpg
#lines = np.array([[[311,1,345,1]],[[320,8,352,8]],[[308,12,339,12]],[[318,22,344,22]],[[318,34,371,33]],[[307,61,391,58]],[[311,94,412,89]]])

# for camera5.jpg
#lines = np.array([[[261,150,306,150]],[[261,101,284,101]],[[311,102,337,103]],[[248,228,280,230]],[[309,233,347,234]],[[382,235,449,232]],[[342,150,439,151]],[[394,107,433,111]],[[324,3,365,3]],[[331,8,362,8]],[[283,48,307,48]]])

print("original lines array: ", lines.shape)
print(lines)

i = 0
for line in lines:
    for x1,y1,x2,y2 in line:
        if abs(y1-y2)>3:
            lines = np.delete(lines, i, axis=0)
        else:
            cv2.line(img,(x1,y1),(x2,y2),(255,0,0),1)
            i+=1

print("after deletes lines array: ", lines.shape)
print(lines)

cv2.imwrite('lines.jpg',img)
im = Image.open('lines.jpg')
im.show()
