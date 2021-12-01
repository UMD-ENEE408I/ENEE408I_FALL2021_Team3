import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
from PIL import Image

# Regular Houghlines with center line detection
ret = np.load("./Calibration/camera2_params/ret.npy")
mtx = np.load("./Calibration/camera2_params/mtx.npy")
dist = np.load("./Calibration/camera2_params/dist.npy")
rvecs = np.load("./Calibration/camera2_params/rvecs.npy")
tvecs = np.load("./Calibration/camera2_params/tvecs.npy")
newmtx = np.load("./Calibration/camera2_params/newmtx.npy")

img_uncal = cv2.imread('15cm.jpg')                          # read image
og_img = cv2.undistort(img_uncal, mtx, dist, None, newmtx)
c = 0.5                                                     # crop factor
c_h = 50
# print("center: ", og_img[17 + int(len(og_img)*c)][336 + 10])
og_img_cp = og_img.copy()
                                                            # 59mm3_T_cal
                                                            # 60mm3_T_cal
                                                            # 92mm
                                                            # 70mm3_end_cal
                                                            # 83mm3_left_cal
                                                            # 88mm3_T_cal
                                                            # 100mm3_right_cal

img = og_img[int(len(og_img)*c):len(og_img)-40, c_h:len(og_img[0])-c_h]      # crop image
print("img dimensions: xLen = ", len(img[0]), "\tyLen = ", len(img))
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)                 # convert cropped image to grayscale
og_gray = cv2.cvtColor(og_img,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,200,255)                             # edge detection with Canny
cv2.imwrite('edges.jpg',edges)                              # write edges to image
lines = cv2.HoughLines(edges,1,np.pi/180,20)                # detect lines
# print("All lines: ")
# print(lines)
# print(lines.shape)

# Display all lines
# for line in lines:
#     for rho,theta in line:
#         a = np.cos(theta)
#         b = np.sin(theta)
#         x0 = a*rho
#         y0 = b*rho
#         x1 = int(x0 + 1000*(-b))
#         y1 = int(y0 + 1000*(a))
#         x2 = int(x0 - 1000*(-b))
#         y2 = int(y0 - 1000*(a))
#         cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
# cv2.imwrite('70mm3allLines.jpg',img)

# extract strong lines
strong_lines = np.zeros([4,1,2])        # [posVert, negVert, horz1, horz2]
# minLineLength = 2
# maxLineGap = 10
# lines = cv2.HoughLines(edges,1,np.pi/180,10, minLineLength, maxLineGap)

n2 = 0
numPosVert = 0
numNegVert = 0
numHorz = 0
for n1 in range(0,len(lines)):
    for rho,theta in lines[n1]:
        if n1 == 0:
            if math.tan(theta) != 0 and -1/math.tan(theta) > 1:
                strong_lines[0] = lines[n1]
                numPosVert += 1
            elif math.tan(theta) != 0 and -1/math.tan(theta) < -1:
                strong_lines[1] = lines[n1]
                numNegVert += 1
            elif math.tan(theta) != 0 and abs(1/math.tan(theta)) < 0.5 :
                strong_lines[2] = lines[n1]
                numHorz += 1
            n2 = n2 + 1
        else:
            if rho < 0:
               rho*=-1
               theta-=np.pi
            # print("rho = ", rho, " theta = ", theta)
            closeness_rho = np.isclose(rho,strong_lines[0:n2,0,0],atol = 10)
            closeness_theta = np.isclose(theta,strong_lines[0:n2,0,1],atol = np.pi/36)
            closeness = np.all([closeness_rho,closeness_theta],axis=0)

            #
            if not any(closeness) and n2 < 4:                                   # check if potential strong line
                if math.tan(theta) != 0 and -1/math.tan(theta) > 1 and numPosVert == 0:                  # check if pos vertical and no pos vert found
                    strong_lines[0] = lines[n1]
                    numPosVert += 1
                    n2 += 1
                elif math.tan(theta) != 0 and -1/math.tan(theta) < -1 and numNegVert == 0:
                    strong_lines[1] = lines[n1]
                    numNegVert += 1
                    n2 += 1
                elif math.tan(theta) != 0 and abs(1/math.tan(theta)) < 0.5 and numHorz < 2:                # check if horiz line and < 2 strong horizs
                    #strong_lines = np.concatenate((strong_lines, [lines[n1]]), axis=0)
                    strong_lines[2 + numHorz] = lines[n1]
                    numHorz += 1
                    n2 += 1

print("numHorz = ", numHorz)

print("strong lines before deletion: ")
print(strong_lines)
print(strong_lines.shape)

# n = 3
# while n >= 0:
#     for rho,theta in strong_lines[n]:
#         if rho < 0.01 and theta < 0.01:
#             print("deleting")
#             strong_lines = np.delete(strong_lines, n, 0)
#         n -= 1

if numHorz < 2:
    for n in range(numHorz + 2, 4):
        #print("deleting n = ", 5-n)
        strong_lines = np.delete(strong_lines, len(strong_lines)-1, 0)

print("strong lines after deletion: ")
print(strong_lines)

# Display strong lines
for line in strong_lines:
    for rho,theta in line:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(img,(x1,y1),(x2,y2),(255,0,0),2)
cv2.imwrite('strongLines.jpg',img)
im = Image.open('strongLines.jpg')
im.show()


# Calculate center line
i = 0
coords = []
for i in range(0,2):
    for rho,theta in strong_lines[i]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        print("(", x1, ", ", y1, "), (", x2, ", ", y2, ")")
        slope = -1/math.tan(theta)
        y3 = 0
        x3 = (y3 - y2)/slope + x2
        y4 = 1000
        x4 = (y4 - y2)/slope + x2
        coords.append([x3, y3, x4, y4])
        #cv2.line(img,(x1,y1),(x2,y2),(50,50,50),2)

c_line_y1 = 0
c_line_y2 = 1000

c_line_x1 = int((coords[0][0] + coords[1][0])/2)
c_line_x2 = int((coords[0][2] + coords[1][2])/2)

cSlope = (c_line_y2 - c_line_y1)/(c_line_x2 - c_line_x1)


# # Calculate horizontal midline: distance based MIGHT NOT NEED
# if numHorz > 0:
#     hCoords = []
#     for i in range(2,numHorz + 1):
#         for rho,theta in line:
#             a = np.cos(theta)
#             b = np.sin(theta)
#             x0 = a*rho
#             y0 = b*rho
#             x1 = int(x0 + 1000*(-b))
#             y1 = int(y0 + 1000*(a))
#             x2 = int(x0 - 1000*(-b))
#             y2 = int(y0 - 1000*(a))
#             print("(", x1, ", ", y1, "), (", x2, ", ", y2, ")")
#             slope = -1/math.tan(theta)
#             x3 = 0
#             y3 = (x3 - x2)*slope + y2
#             x4 = 1000
#             y4 = (x4 - x2)*slope + y2
#             hCoords.append([x3, y3, x4, y4])
#             cv2.line(img,(x1,y1),(x2,y2),(0,0,50),2)
#             i += 1
#
#     cv2.imwrite('h_lines.jpg',img)
#     im = Image.open('h_lines.jpg')
#
#     if numHorz > 1:
#         hCoords[0][1] = int((hCoords[0][1] + hCoords[1][1])/2)
#         hCoords[0][3] = int((hCoords[0][3] + hCoords[1][3])/2)
#         hSlope = (hCoords[0][1] - hCoords[0][3])/(hCoords[0][0] - hCoords[0][2])
#
#     if numHorz > 1:
#         def intersection(l1, l2):
#             rho1, theta1 = l1[0]
#             rho2, theta2 = l2[0]
#             A = np.array([
#                 [np.cos(theta1), np.sin(theta1)],
#                 [np.cos(theta2), np.sin(theta2)]])
#             b = np.array([[rho1], [rho2]])
#             x0, y0 = np.linalg.solve(A, b)
#             x0, y0 = int(np.round(x0)), int(np.round(y0))
#             return [[x0, y0]]
#
#         # Calculate 4 corners of intersection
#         corners = []
#         i = 0
#         while i < 2:
#             j = 2
#             while j < 2 + numHorz:
#                 corners.append(intersection(strong_lines[i], strong_lines[j]))
#                 j += 1
#             i += 1
#
#
#         # print and display corner points
#         print(corners)
#         k = 0
#         for point in corners:
#             for x,y in point:
#                 cv2.circle(img,(x,y),radius=1,color=(0,0,255),thickness=2)
#                 d = 120*pow(2.5,-0.02*y)+20
#                 print("distance to intersect ", k, ": ", d, " mm")
#                 k += 1
#
#
#         # Calculate midline of intersecting path
#         if numHorz > 1:
#             int_d1 = 120*pow(2.5,-0.02*corners[0][0][1])+20
#             int_d2 = 120*pow(2.5,-0.02*corners[1][0][1])+20
#             print("int dist 1: ", int_d1, "\tint dist 2: ", int_d2)
#
#             int_dmid = 0        # distance in mm to midline
#             if int_d1 < int_d2:
#                 int_dmid = int_d1 + (int_d2 - int_d1)/2
#             else :
#                 int_dmid = int_d2 + (int_d1 - int_d2)/2
#
#             int_ymid = int(-50*math.log((int_dmid - 20)/120, 2.5))      # y pixel coordinate for midline
#             print("int dist midpoint: ", int_dmid, "\tint y midpoint: ", int_ymid)
#             cv2.line(img,(0,int_ymid),(1000,int_ymid),(0,255,0),2)
#
#             # Calculate center point of intersection
#             int_center_x = int(int_ymid/1000*(c_line_x2 - c_line_x1) + c_line_x1)
#             cv2.circle(img,(int_center_x,int_ymid),radius=1,color=(0,0,255),thickness=2)

# Calculate horizontal midline: pixel coord based
if numHorz > 0 :
    print("numHorz > 0")
    def intersection(l1, l2):
        rho1, theta1 = l1[0]
        rho2, theta2 = l2[0]
        A = np.array([
            [np.cos(theta1), np.sin(theta1)],
            [np.cos(theta2), np.sin(theta2)]])
        b = np.array([[rho1], [rho2]])
        x0, y0 = np.linalg.solve(A, b)
        x0, y0 = int(np.round(x0)), int(np.round(y0))
        return [[x0, y0]]

    if numHorz > 1 :    # Both intersecting edges present
        print("numHorz > 1")
        # Calculate 4 corners of intersection
        corners = []
        i = 0
        while i < 2:
            j = 2
            while j < 2 + numHorz:
                corners.append(intersection(strong_lines[i], strong_lines[j]))
                j += 1
            i += 1

        # Calculate center of intersection
        centerX = int((corners[0][0][0] + corners[2][0][0] + corners[1][0][0] + corners[3][0][0])/4)
        centerY = int((corners[0][0][1] + corners[2][0][1] + corners[1][0][1] + corners[3][0][1])/4)

    else :              # One intersecting edge present; center is average of intersections
        print("numHorz = 1")
        corners = [intersection(strong_lines[0], strong_lines[2]), intersection(strong_lines[1], strong_lines[2])]
        centerX = int((corners[0][0][0] + corners[1][0][0])/2)
        centerY = int((corners[0][0][1] + corners[1][0][1])/2)

else :
    centerY = int(len(img)/2)
    coords = []
    for line in strong_lines:
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            print("(", x1, ", ", y1, "), (", x2, ", ", y2, ")")
            slope = -1/math.tan(theta)
            y3 = centerY
            x3 = (y3 - y2)/slope + x2
            coords.append(x3)
        print("coords: ")
        print(coords)
    centerX = int((coords[0] + coords[1])/2)

# cv2.circle(img,(100,100),radius=1,color=(0,255,0),thickness=3)
# cv2.imwrite('circleTest.jpg',img)
#
print("centerX = ", centerX, "\txDim = ", len(img[0]))
print("centerY = ", centerY, "\tyDim = ", len(img))
cv2.circle(img,(centerX,centerY),radius=1,color=(0,255,0),thickness=2)


left = 0
right = 0
up = 0
down = 0

# Check left of center
centerL = centerX - 70
cv2.circle(og_img,(centerL + c_h,centerY + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
# cv2.circle(og_img,(centerL,centerY),radius=1,color=(0,0,255),thickness=2)
# cv2.circle(img,(centerL,centerY),radius=1,color=(0,0,255),thickness=2)
if og_gray[centerY + int(len(og_img)*c)][centerL + c_h] > 200 :
    left = 1

# Check right of center
centerR = centerX + 70
cv2.circle(og_img,(centerR + c_h,centerY + int(len(og_img)*c)),radius=1,color=(0,0,100),thickness=2)
# cv2.circle(og_img,(centerR,centerY),radius=1,color=(0,0,255),thickness=2)
# cv2.circle(img,(centerR,centerY),radius=1,color=(0,0,255),thickness=2)
if og_gray[centerY + int(len(og_img)*c)][centerR + c_h] > 200 :
    right = 1

# Check 20mm above center
deltaU = int(math.log(1/60 + math.pow(2.8,-0.02*centerY),2.8)/-0.02)        # calculate pixel difference
if deltaU == 0 :
    deltaU = 15
print("deltaU = ", deltaU)
centerU = centerY - deltaU
cv2.circle(og_img,(centerX + c_h,centerU + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
# cv2.circle(og_img,(centerX,centerU),radius=1,color=(0,0,255),thickness=2)
# cv2.circle(img,(centerX,centerU),radius=1,color=(0,0,255),thickness=2)
if og_gray[centerU + int(len(og_img)*c)][centerX + c_h] > 200 :
    up = 1

# Check 20mm below center
deltaD = int(math.log(math.pow(2.8,-0.02*centerY) - 1/60,2.8)/-0.02)        # calculate pixel difference
if deltaD == 0 :
    deltaD = 15
print("deltaD = ", deltaD)
centerD = centerY + deltaD
cv2.circle(og_img,(centerX + c_h,centerD + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
# cv2.circle(og_img,(centerX,centerD),radius=1,color=(0,0,255),thickness=2)
# cv2.circle(img,(centerX,centerD),radius=1,color=(0,0,255),thickness=2)
if og_gray[centerD + int(len(og_img)*c)][centerX + c_h] > 200 :
    down = 1

print("samplePoints:")
# print("center: ", og_img_cp[centerY + int(len(og_img)*c)][centerX + 10])
# print("up: ", og_img_cp[centerU + int(len(og_img)*c)][centerX + 10])
# print("down: ", og_img_cp[centerD + int(len(og_img)*c)][centerX + 10])
# print("left: ", og_img_cp[centerY + int(len(og_img)*c)][centerL + 10])
# print("right: ", og_img_cp[centerY + int(len(og_img)*c)][centerR + 10])
print("center: ", og_gray[centerY + int(len(og_img)*c)][centerX + c_h] > 200)
print("up: ", og_gray[centerU + int(len(og_img)*c)][centerX + c_h] > 200)
print("down: ", og_gray[centerD + int(len(og_img)*c)][centerX + c_h] > 200)
print("left: ", og_gray[centerY + int(len(og_img)*c)][centerL + c_h] > 200)
print("right: ", og_gray[centerY + int(len(og_img)*c)][centerR + c_h] > 200)
print("up left: ", og_gray[centerU + int(len(og_img)*c)][centerL + c_h] > 200)
print("up right: ", og_gray[centerU + int(len(og_img)*c)][centerR + c_h] > 200)
print("down left: ", og_gray[centerD + int(len(og_img)*c)][centerL + c_h] > 200)
print("down right: ", og_gray[centerD + int(len(og_img)*c)][centerR + c_h] > 200)

cv2.imwrite('samplePoints.jpg',img)
cv2.imwrite('og_samplePoints.jpg',og_img)
#im = Image.open('samplePoints.jpg')
#im.show()
print("left, right, up, down: ", left, ", ", right, ", ", up, ", ", down)


type = -1
binary = 8*left + 4*right + 2*up + down
print("binary = ", binary)
print()
if og_gray[centerU + int(len(og_img)*c)][centerL + c_h] > 200 or og_gray[centerU + int(len(og_img)*c)][centerR + c_h] > 200 or og_gray[centerD + int(len(og_img)*c)][centerL + c_h] > 200 or og_gray[centerD + int(len(og_img)*c)][centerR + c_h] > 200:
    type = 8
    print("END")
elif binary == 3:
    type = 0
    print("straight")
elif binary == 15:
    type = 1
    print("cross")
elif binary == 13:
    type = 2
    print("straight T")
elif binary == 7:
    type = 3
    print("right T")
elif binary == 11:
    type = 4
    print("left T")
elif binary == 9:
    type = 5
    print("left corner")
elif binary == 5:
    type = 6
    print("right corner")
elif binary == 1:
    type = 7
    print("end")
else :
    print("error")

    # print("pixel left of center: ", gray[int_ymid][int_center_left])
    # print("pixel up and left of center: ", gray[int_ymid-100][int_center_left])

# # Begin selecting path edges
# i = 0
# maxSlope_ind = 0
# maxSlope = 0
# minSlope_ind = 0
# minSlope = 0
#
# n = 0       # n = number of horizontal lines
#
# # Find most vertical lines (most positive and most negative)
# # Find slope closest to zero
# #print("slopes: ")
# for line in lines:
#     for rho,theta in line:
#         print("rho = ", rho, ", theta = ", theta)
#         if theta != 0:
#             slope =  -1/math.tan(theta)
#             print("\tslope = ", slope)
#
#             if slope>maxSlope:
#                 maxSlope = slope
#                 maxSlope_ind = i
#             elif slope<minSlope:
#                 minSlope = slope
#                 minSlope_ind = i
#             if abs(slope) < 0.1:
#                 n += 1
#         i += 1
#
# # Make new array with only main path and intersection path edges
# # Initialize array to main path edges
# slopes = [maxSlope, minSlope]
# kept_lines = np.stack((lines[maxSlope_ind], lines[minSlope_ind]))
# print("kept_lines before adding intLines: ")
# print(kept_lines)
# print("\tsize: ", kept_lines.shape)
# print("indices: ", maxSlope_ind, ", ", minSlope_ind)
# print()
#
# i = 0
# coords = []
# for line in kept_lines:
#     for rho,theta in line:
#         a = np.cos(theta)
#         b = np.sin(theta)
#         x0 = a*rho
#         y0 = b*rho
#         x1 = int(x0 + 1000*(-b))
#         y1 = int(y0 + 1000*(a))
#         x2 = int(x0 - 1000*(-b))
#         y2 = int(y0 - 1000*(a))
#         print("(", x1, ", ", y1, "), (", x2, ", ", y2, ")")
#         y3 = 0
#         x3 = (y3 - y2)/slopes[i] + x2
#         y4 = 1000
#         x4 = (y4 - y2)/slopes[i] + x2
#         coords.append([x3, y3, x4, y4])
#         #cv2.line(img,(x1,y1),(x2,y2),(50,50,50),2)
#         i += 1
#
# c_line_y1 = 0
# c_line_y2 = 1000
#
# c_line_x1 = int((coords[0][0] + coords[1][0])/2)
# c_line_x2 = int((coords[0][2] + coords[1][2])/2)
#
# cSlope = (c_line_y2 - c_line_y1)/(c_line_x2 - c_line_x1)
#
# print("c_line: ")
# print("(", c_line_x1, ", ", c_line_y1, "), (", c_line_x2, ", ", c_line_y2, ")")
# cv2.line(img,(c_line_x1,c_line_y1),(c_line_x2,c_line_y2),(255,0,0),2)
#
# intLines = 0    # intLines=0 if no intersecting lines
# if n > 1:       # There are at least 2 potential intersection lines
#     print("There are intersecting lines")
#
#     zeroSlope = 100                         # find most horizontal slope
#     zeroSlope_ind = -1
#     i = 0
#     for line in lines:
#         for rho,theta in line:
#             if theta != 0:
#                 slope =  -1/math.tan(theta)
#
#                 if abs(slope)<abs(zeroSlope):
#                     zeroSlope = slope
#                     zeroSlope_ind = i
#             i += 1
#
#     print("zeroSlope_ind: ", zeroSlope_ind)
#     print("zeroSlope line: ", lines[zeroSlope_ind])
#     int_x = (zeroSlope*lines[zeroSlope_ind][0][0] - lines[zeroSlope_ind][0][1] - cSlope*c_line_x1 + c_line_y2)/(zeroSlope - cSlope)
#     int_y = zeroSlope*(int_x - lines[zeroSlope_ind][0][0]) + lines[zeroSlope_ind][0][1]
#
#     i = 0
#     zeroSlope2 = 100
#     for line in lines:
#         for rho,theta in line:
#             if i != zeroSlope_ind:
#                 if theta != 0:          # Ignore perfectly vertical lines
#                     slope =  -1/math.tan(theta)
#                     print("zeroSlope2 = ", zeroSlope2, "\tslope = ", slope)
#                     print("\trho = ", rho, "\tzeroSlope rho = ", lines[zeroSlope_ind][0][0])
#
#                     int2_y = (slope*c_line_y1 - cSlope*lines[i][0][1] + slope*cSlope*(lines[i][0][0] - c_line_x1))/(slope - cSlope)
#                     if abs(int2_y - int_y) > 5 and abs(slope)<abs(zeroSlope2):
#                         print("\tintLines=1")
#                         zeroSlope2 = slope
#                         zeroSlope2_ind = i
#                         intLines = 1
#
#                     # if abs(slope)<abs(zeroSlope2) and abs(rho-lines[zeroSlope_ind][0][0])>5:
#                     #     print("\tintLines=1")
#                     #     zeroSlope2 = slope
#                     #     zeroSlope2_ind = i
#                     #     intLines = 1    # intLines=1 if intersecting lines present
#             i += 1
#
#     print("zeroSlope: ", zeroSlope, " @ i=", zeroSlope_ind, ", zeroSlope2: ", zeroSlope2, " @ i=", zeroSlope2_ind)
#
#     hLines = np.stack((lines[zeroSlope_ind], lines[zeroSlope2_ind]))
#     hSlopes = [zeroSlope, zeroSlope2]
#     hCoords = []
#     i = 0
#     for line in hLines:
#         for rho,theta in line:
#             a = np.cos(theta)
#             b = np.sin(theta)
#             x0 = a*rho
#             y0 = b*rho
#             x1 = int(x0 + 1000*(-b))
#             y1 = int(y0 + 1000*(a))
#             x2 = int(x0 - 1000*(-b))
#             y2 = int(y0 - 1000*(a))
#             print("(", x1, ", ", y1, "), (", x2, ", ", y2, ")")
#             x3 = 0
#             y3 = (x3 - x2)*hSlopes[i] + y2
#             x4 = 1000
#             y4 = (x4 - x2)*hSlopes[i] + y2
#             hCoords.append([x3, y3, x4, y4])
#             cv2.line(img,(x1,y1),(x2,y2),(0,0,50),2)
#             i += 1
#
#     cv2.imwrite('h_lines.jpg',img)
#     im = Image.open('h_lines.jpg')
#
#     h_line_x1 = 0
#     h_line_x2 = 1000
#     h_line_y1 = int((hCoords[0][1] + hCoords[1][1])/2)
#     h_line_y2 = int((hCoords[0][3] + hCoords[1][3])/2)
#     hSlope = (h_line_y2 - h_line_y1)/(h_line_x2 - h_line_x1)
#
# # Append intersection path edges if present
# if intLines == 1:
#     print("appending horizontal lines")
#     kept_lines = np.concatenate((kept_lines, [lines[zeroSlope_ind]]), axis=0)
#     kept_lines = np.concatenate((kept_lines, [lines[zeroSlope2_ind]]), axis=0)
#     print("kept_lines: ")
#     print(kept_lines)
#     slopes.append(zeroSlope)
#     slopes.append(zeroSlope2)
#     print("slopes: ")
#     print(slopes)
#     print()
#
#
# # Derive vertical centerline from main path edges
# # der_coords = []
# #
# # i = 0
# # for line in kept_lines:
# #     for rho,theta in line:
# #         a = np.cos(theta)
# #         b = np.sin(theta)
# #         x0 = a*rho
# #         y0 = b*rho
# #         x1 = int(x0 + 1000*(-b))
# #         y1 = int(y0 + 1000*(a))
# #         x2 = int(x0 - 1000*(-b))
# #         y2 = int(y0 - 1000*(a))
# #         print("(", x1, ", ", y1, "), (", x2, ", ", y2, ")")
# #         y3 = 0
# #         x3 = (y3 - y2)/slopes[i] + x2
# #         y4 = 1000
# #         x4 = (y4 - y2)/slopes[i] + x2
# #         der_coords.append([x3, y3, x4, y4])
# #         cv2.line(img,(x1,y1),(x2,y2),(50,50,50*i),2)
# #         i = i+1
# #
# # print("der_coords: ")
# # print(der_coords)
# #
# # c_line_y1 = 0
# # c_line_y2 = 1000
# #
# # c_line_x1 = int((der_coords[0][0] + der_coords[1][0])/2)
# # c_line_x2 = int((der_coords[0][2] + der_coords[1][2])/2)
# #
# # print("c_line: ")
# # print("(", c_line_x1, ", ", c_line_y1, "), (", c_line_x2, ", ", c_line_y2, ")")
# # cv2.line(img,(c_line_x1,c_line_y1),(c_line_x2,c_line_y2),(255,0,0),2)
#
# # Find intersection points if intersecting path is present
# if intLines == 1:       # There are intersections
#
#     def intersection(l1, l2):
#         rho1, theta1 = l1[0]
#         rho2, theta2 = l2[0]
#         A = np.array([
#             [np.cos(theta1), np.sin(theta1)],
#             [np.cos(theta2), np.sin(theta2)]])
#         b = np.array([[rho1], [rho2]])
#         x0, y0 = np.linalg.solve(A, b)
#         x0, y0 = int(np.round(x0)), int(np.round(y0))
#         return [[x0, y0]]
#
#     # Calculate 4 corners of intersection
#     corners = []
#     i = 0
#     while i<2:
#         j = 2
#         while j<4:
#             corners.append(intersection(kept_lines[i], kept_lines[j]))
#             j = j+1
#         i = i+1
#
#
#     # print and display corner points
#     print(corners)
#     k = 0
#     for point in corners:
#         for x,y in point:
#             cv2.circle(img,(x,y),radius=1,color=(0,0,255),thickness=2)
#             d = 120*pow(2.5,-0.02*y)+20
#             print("distance to intersect ", k, ": ", d, " mm")
#             k+=1
#
#     # Calculate midline of intersecting path
#     int_d1 = 120*pow(2.5,-0.02*corners[0][0][1])+20
#     int_d2 = 120*pow(2.5,-0.02*corners[1][0][1])+20
#     print("int dist 1: ", int_d1, "\tint dist 2: ", int_d2)
#
#     int_dmid = 0        # distance in mm to midline
#     if int_d1 < int_d2:
#         int_dmid = int_d1 + (int_d2 - int_d1)/2
#     else :
#         int_dmid = int_d2 + (int_d1 - int_d2)/2
#
#     int_ymid = int(-50*math.log((int_dmid - 20)/120, 2.5))      # y pixel coordinate for midline
#     print("int dist midpoint: ", int_dmid, "\tint y midpoint: ", int_ymid)
#     cv2.line(img,(0,int_ymid),(1000,int_ymid),(0,255,0),2)
#
#     # Calculate center point of intersection
#     int_center_x = int(int_ymid/1000*(c_line_x2 - c_line_x1) + c_line_x1)
#     cv2.circle(img,(int_center_x,int_ymid),radius=1,color=(0,0,255),thickness=2)
#
#     left = 0
#     right = 0
#     up = 0
#     down = 0
#
#     # Check left of center
#     int_center_left = int_center_x - 100
#     cv2.circle(img,(int_ymid,int_center_left),radius=1,color=(0,0,255),thickness=2)
#     if gray[int_ymid][int_center_left] > 200 :
#         left = 1
#
#     # Check right of center
#     int_center_right = int_center_x + 100
#     cv2.circle(img,(int_ymid,int_center_right),radius=1,color=(0,0,255),thickness=2)
#     if gray[int_ymid][int_center_right] > 200 :
#         right = 1
#
#     # Check above center
#     int_center_up = int_ymid - 40
#     cv2.circle(img,(int_center_x,int_center_up),radius=1,color=(0,0,255),thickness=2)
#     if gray[int_center_up][int_center_x] > 200 :
#         up = 1
#
#     # Check below center
#     int_center_down = int_ymid + 70
#     cv2.circle(img,(int_center_x,int_center_down),radius=1,color=(0,0,255),thickness=2)
#     cv2.imwrite('samplePoints.jpg',img)
#     im = Image.open('samplePoints.jpg')
#     if gray[int_center_down][int_center_x] > 200 :
#         down = 1
#
#     print("left, right, up, down: ", left, ", ", right, ", ", up, ", ", down)
#
#     print("pixel left of center: ", gray[int_ymid][int_center_left])
#     print("pixel up and left of center: ", gray[int_ymid-100][int_center_left])
#
#
# cv2.imwrite('c_line_intersects.jpg',img)
# im = Image.open('c_line_intersects.jpg')
# im.show()
