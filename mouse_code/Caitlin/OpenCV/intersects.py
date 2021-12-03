import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
from PIL import Image



# Load calibration values
ret = np.load("./Calibration/camera2_params/ret.npy")
mtx = np.load("./Calibration/camera2_params/mtx.npy")
dist = np.load("./Calibration/camera2_params/dist.npy")
rvecs = np.load("./Calibration/camera2_params/rvecs.npy")
tvecs = np.load("./Calibration/camera2_params/tvecs.npy")
newmtx = np.load("./Calibration/camera2_params/newmtx.npy")

# Load image
img_uncal = cv2.imread('15cm.jpg')                          # Read uncalibrated image
                                                            # 59mm3_T_cal
                                                            # 60mm3_T_cal
                                                            # 92mm
                                                            # 70mm3_end_cal
                                                            # 83mm3_left_cal
                                                            # 88mm3_T_cal
                                                            # 100mm3_right_cal

og_img = cv2.undistort(img_uncal, mtx, dist, None, newmtx)  # Undistort image
og_img_cp = og_img.copy()                                   # Copy undistorted, uncropped image
og_gray = cv2.cvtColor(og_img,cv2.COLOR_BGR2GRAY)           # convert uncropped image to grayscale

c = 0.5                                                     # Vertical crop factor
c_h = 50                                                    # Horizontal crop amount

img = og_img[int(len(og_img)*c):len(og_img)-40, c_h:len(og_img[0])-c_h]     # crop image
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)                 # convert cropped image to grayscale
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

if lines is not None:
    # Extract strong lines
    strong_lines = np.zeros([4,1,2])        # format: [posVert, negVert, horz1, horz2]

    n2 = 0
    numPosVert = 0
    numNegVert = 0
    numHorz = 0
    for n1 in range(0,len(lines)):
        for rho,theta in lines[n1]:
            if n1 == 0:                                                 # Classify strongest line
                if math.tan(theta) != 0 and -1/math.tan(theta) > 1:     # Store as positive slope vertical line
                    strong_lines[0] = lines[n1]
                    numPosVert += 1
                elif math.tan(theta) != 0 and -1/math.tan(theta) < -1:  # Store as negative slope vertical line
                    strong_lines[1] = lines[n1]
                    numNegVert += 1
                elif math.tan(theta) != 0 and abs(1/math.tan(theta)) < 0.5 and (-1/math.tan(theta)*(int(len(img[0])/2) - np.cos(theta)*rho) + np.sin(theta)*rho) > 0:    # Store as first horizontal line
                    strong_lines[2] = lines[n1]
                    numHorz += 1
                n2 = n2 + 1
            else:                                                       # Classify remaining lines
                if rho < 0:
                   rho*=-1
                   theta-=np.pi
                # print("rho = ", rho, " theta = ", theta)
                closeness_rho = np.isclose(rho,strong_lines[0:n2,0,0],atol = 10)
                closeness_theta = np.isclose(theta,strong_lines[0:n2,0,1],atol = np.pi/36)
                closeness = np.all([closeness_rho,closeness_theta],axis=0)

                if not any(closeness) and n2 < 4:                                   # Classify line if not close to other strong lines and strong_lines not full
                    if math.tan(theta) != 0 and -1/math.tan(theta) > 1 and numPosVert == 0:                 # Check if line is pos vertical, store if no pos vertical already found
                        strong_lines[0] = lines[n1]
                        numPosVert += 1
                        n2 += 1
                    elif math.tan(theta) != 0 and -1/math.tan(theta) < -1 and numNegVert == 0:              # Check if line is neg vertical, store if no neg vertical already found
                        strong_lines[1] = lines[n1]
                        numNegVert += 1
                        n2 += 1
                    elif math.tan(theta) != 0 and abs(1/math.tan(theta)) < 0.5 and and (-1/math.tan(theta)*(int(len(img[0])/2) - np.cos(theta)*rho) + np.sin(theta)*rho) > 0 and numHorz < 2:             # Check if horiz line, store if <2 horizontals already found
                        if numHorz > 0:
                            if abs((-1/math.tan(theta)*(int(len(img[0])/2) - np.cos(theta)*rho) + np.sin(theta)*rho) - (-1/math.tan(strong_lines[2][0][1])*(int(len(img[0])/2) - np.cos(strong_lines[2][0][1])*strong_lines[2][0][0]) + np.sin(strong_lines[2][0][1])*strong_lines[2][0][0])) > 10:
                                strong_lines[2 + numHorz] = lines[n1]
                                numHorz += 1
                                n2 += 1

    print("numHorz = ", numHorz)

    print("strong lines before deletion: ")
    print(strong_lines)
    print(strong_lines.shape)

    # Remove unused strong_lines elements (for when <2 horizontal lines found)
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


    # # Calculate center line (unnecessary atm)
    # i = 0
    # coords = []
    # for i in range(0,2):
    #     for rho,theta in strong_lines[i]:
    #         a = np.cos(theta)
    #         b = np.sin(theta)
    #         x0 = a*rho
    #         y0 = b*rho
    #         x1 = int(x0 + 1000*(-b))
    #         y1 = int(y0 + 1000*(a))
    #         x2 = int(x0 - 1000*(-b))
    #         y2 = int(y0 - 1000*(a))
    #         print("(", x1, ", ", y1, "), (", x2, ", ", y2, ")")
    #         slope = -1/math.tan(theta)
    #         y3 = 0
    #         x3 = (y3 - y2)/slope + x2
    #         y4 = 1000
    #         x4 = (y4 - y2)/slope + x2
    #         coords.append([x3, y3, x4, y4])
    #         #cv2.line(img,(x1,y1),(x2,y2),(50,50,50),2)
    #
    # c_line_y1 = 0
    # c_line_y2 = 1000
    #
    # c_line_x1 = int((coords[0][0] + coords[1][0])/2)
    # c_line_x2 = int((coords[0][2] + coords[1][2])/2)
    #
    # cSlope = (c_line_y2 - c_line_y1)/(c_line_x2 - c_line_x1)


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

    # Calculate center point

    # If at least one horizontal present
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

        # All 4 lines present
        if numHorz > 1 :
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

        # One horizontal edge present
        # Center is average of two intersections
        else :
            print("numHorz = 1")
            corners = [intersection(strong_lines[0], strong_lines[2]), intersection(strong_lines[1], strong_lines[2])]
            centerX = int((corners[0][0][0] + corners[1][0][0])/2)
            centerY = int((corners[0][0][1] + corners[1][0][1])/2)

    # No horizontal edges present
    # Center is halfway down image and halfway between two vertical edges
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

    print("centerX = ", centerX, "\txDim = ", len(img[0]))
    print("centerY = ", centerY, "\tyDim = ", len(img))
    cv2.circle(img,(centerX,centerY),radius=1,color=(0,255,0),thickness=2)


    # Sample image and determine intersection type
    left = 0
    right = 0
    up = 0
    down = 0

    # Check left of center
    centerL = centerX - 70
    cv2.circle(og_img,(centerL + c_h,centerY + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
    if og_gray[centerY + int(len(og_img)*c)][centerL + c_h] > 200 :
        left = 1

    # Check right of center
    centerR = centerX + 70
    cv2.circle(og_img,(centerR + c_h,centerY + int(len(og_img)*c)),radius=1,color=(0,0,100),thickness=2)
    if og_gray[centerY + int(len(og_img)*c)][centerR + c_h] > 200 :
        right = 1

    # Check 20mm above center
    deltaU = int(math.log(1/60 + math.pow(2.8,-0.02*centerY),2.8)/-0.02)        # calculate pixel difference
    if deltaU == 0 :
        deltaU = 15
    print("deltaU = ", deltaU)
    centerU = centerY - deltaU
    cv2.circle(og_img,(centerX + c_h,centerU + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
    if og_gray[centerU + int(len(og_img)*c)][centerX + c_h] > 200 :
        up = 1

    # Check 20mm below center
    deltaD = int(math.log(math.pow(2.8,-0.02*centerY) - 1/60,2.8)/-0.02)        # calculate pixel difference
    if deltaD == 0 :
        deltaD = 15
    print("deltaD = ", deltaD)
    centerD = centerY + deltaD
    cv2.circle(og_img,(centerX + c_h,centerD + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
    if og_gray[centerD + int(len(og_img)*c)][centerX + c_h] > 200 :
        down = 1

    print("samplePoints:")
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
