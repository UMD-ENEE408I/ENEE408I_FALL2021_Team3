import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
from PIL import Image

# Regular Houghlines with center line detection

img = cv2.imread('59mm3_T_calib.jpg')                          # read image
img = img[int(len(img)*0.6):len(img)-40, 10:len(img[0])-10]      # crop image
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)                 # convert to grayscale
edges = cv2.Canny(gray,200,255)                             # edge detection with Canny
cv2.imwrite('edges.jpg',edges)                              # write edges to image
lines = cv2.HoughLines(edges,1,np.pi/180,50)                # detect lines
print("All lines: ")
print(lines)

# Calculate coordinates for all detected lines
for line in lines:
    for rho,theta in line:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

cv2.imwrite('allLines.jpg',edges)

# Begin selecting path edges
i = 0
maxSlope_ind = 0
maxSlope = 0
minSlope_ind = 0
minSlope = 0

n = 0       # n = number of horizontal lines

# Find most vertical lines (most positive and most negative)
# Find slope closest to zero
#print("slopes: ")
for line in lines:
    for rho,theta in line:
        print("rho = ", rho, ", theta = ", theta)
        if theta != 0:
            slope =  -1/math.tan(theta)
            print("\tslope = ", slope)

            if slope>maxSlope:
                maxSlope = slope
                maxSlope_ind = i
            elif slope<minSlope:
                minSlope = slope
                minSlope_ind = i
            if abs(slope) < 0.1:
                n += 1
        i += 1

intLines = 0    # intLines=0 if no intersecting lines

if n > 1:       # There are at least 2 potential intersection lines
    print("There are intersecting lines")

    zeroSlope = 100
    zeroSlope_ind = -1
    i = 0
    for line in lines:
        for rho,theta in line:
            if theta != 0:
                slope =  -1/math.tan(theta)

                if abs(slope)<abs(zeroSlope):
                    zeroSlope = slope
                    zeroSlope_ind = i
            i += 1

    zeroSlope2 = 1
    zeroSlope2_ind = zeroSlope_ind
    i = 0
    for line in lines:
        for rho,theta in line:
            if i != zeroSlope_ind:
                if theta != 0:          # Ignore perfectly vertical lines
                    slope =  -1/math.tan(theta)
                    print("zeroSlope2 = ", zeroSlope2, "\tslope = ", slope)
                    print("\trho = ", rho, "\tzeroSlope rho = ", lines[zeroSlope_ind][0][0])
                    if abs(slope)<abs(zeroSlope2) and abs(rho-lines[zeroSlope_ind][0][0])>5:
                        print("\tintLines=1")
                        zeroSlope2 = slope
                        zeroSlope2_ind = i
                        intLines = 1    # intLines=1 if intersecting lines present
            i += 1

    print("zeroSlope: ", zeroSlope, " @ i=", zeroSlope_ind, ", zeroSlope2: ", zeroSlope2, " @ i=", zeroSlope2_ind)

# Make new array with only main path and intersection path edges
# Initialize array to main path edges
slopes = [maxSlope, minSlope]
kept_lines = np.stack((lines[maxSlope_ind], lines[minSlope_ind]))
print("kept_lines before adding intLines: ")
print(kept_lines)
print("\tsize: ", kept_lines.shape)
print()

# Append intersection path edges if present
if intLines == 1:
    print("appending horizontal lines")
    kept_lines = np.concatenate((kept_lines, [lines[zeroSlope_ind]]), axis=0)
    kept_lines = np.concatenate((kept_lines, [lines[zeroSlope2_ind]]), axis=0)
    print("kept_lines: ")
    print(kept_lines)
    slopes.append(zeroSlope)
    slopes.append(zeroSlope2)
    print("slopes: ")
    print(slopes)
    print()


# Derive vertical centerline from main path edges
der_coords = []

i = 0
for line in kept_lines:
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
        y3 = 0
        x3 = (y3 - y2)/slopes[i] + x2
        y4 = 1000
        x4 = (y4 - y2)/slopes[i] + x2
        der_coords.append([x3, y3, x4, y4])
        cv2.line(img,(x1,y1),(x2,y2),(50,50,50*i),2)
        i = i+1

print("der_coords: ")
print(der_coords)

c_line_y1 = 0
c_line_y2 = 1000

c_line_x1 = int((der_coords[0][0] + der_coords[1][0])/2)
c_line_x2 = int((der_coords[0][2] + der_coords[1][2])/2)

print("c_line: ")
print("(", c_line_x1, ", ", c_line_y1, "), (", c_line_x2, ", ", c_line_y2, ")")
cv2.line(img,(c_line_x1,c_line_y1),(c_line_x2,c_line_y2),(255,0,0),2)

# Find intersection points if intersecting path is present
if intLines == 1:       # There are intersections

    def intersection(l1, l2):
        rho1, theta1 = l1[0]
        rho2, theta2 = l2[0]
        A = np.array([
            [np.cos(theta1), np.sin(theta1)],
            [np.cos(theta2), np.sin(theta2)]
        ])
        b = np.array([[rho1], [rho2]])
        x0, y0 = np.linalg.solve(A, b)
        x0, y0 = int(np.round(x0)), int(np.round(y0))
        return [[x0, y0]]

    # Calculate 4 corners of intersection
    corners = []
    i = 0
    while i<2:
        j = 2
        while j<4:
            corners.append(intersection(kept_lines[i], kept_lines[j]))
            j = j+1
        i = i+1


    # print and display corner points
    print(corners)
    k = 0
    for point in corners:
        for x,y in point:
            cv2.circle(img,(x,y),radius=1,color=(0,0,255),thickness=2)
            d = 120*pow(2.5,-0.02*y)+20
            print("distance to intersect ", k, ": ", d, " mm")
            k+=1

    # Calculate midline of intersecting path
    int_d1 = 120*pow(2.5,-0.02*corners[0][0][1])+20
    int_d2 = 120*pow(2.5,-0.02*corners[1][0][1])+20
    print("int dist 1: ", int_d1, "\tint dist 2: ", int_d2)

    int_dmid = 0        # distance in mm to midline
    if int_d1 < int_d2:
        int_dmid = int_d1 + (int_d2 - int_d1)/2
    else :
        int_dmid = int_d2 + (int_d1 - int_d2)/2

    int_ymid = int(-50*math.log((int_dmid - 20)/120, 2.5))      # y pixel coordinate for midline
    print("int dist midpoint: ", int_dmid, "\tint y midpoint: ", int_ymid)
    cv2.line(img,(0,int_ymid),(1000,int_ymid),(0,255,0),2)

    # Calculate center point of intersection
    int_center_x = int(int_ymid/1000*(c_line_x2 - c_line_x1) + c_line_x1)
    cv2.circle(img,(int_center_x,int_ymid),radius=1,color=(0,0,255),thickness=2)

    left = 0
    right = 0
    up = 0
    down = 0

    # Check left of center
    int_center_left = int_center_x - 100
    if gray[int_ymid][int_center_left] > 200 :
        left = 1

    # Check right of center
    int_center_right = int_center_x + 100
    if gray[int_ymid][int_center_right] > 200 :
        right = 1

    # Check above center
    int_center_up = int_ymid - 40
    cv2.circle(img,(int_center_x,int_center_up),radius=1,color=(0,0,255),thickness=2)
    if gray[int_center_up][int_center_x] > 200 :
        up = 1

    # Check below center
    int_center_down = int_ymid + 100
    if gray[int_center_down][int_center_x] > 200 :
        down = 1

    print("left, right, up, down: ", left, ", ", right, ", ", up, ", ", down)

    print("pixel left of center: ", gray[int_ymid][int_center_left])
    print("pixel up and left of center: ", gray[int_ymid-100][int_center_left])


cv2.imwrite('c_line_intersects.jpg',img)
im = Image.open('c_line_intersects.jpg')
im.show()
