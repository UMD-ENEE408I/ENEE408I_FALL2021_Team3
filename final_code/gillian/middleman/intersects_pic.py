import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
# from PIL import Image

def initialize():
    vid = cv2.VideoCapture(1)
    return vid

def close(vid):
    vid.release()
    cv2.destroyAllWindows()
    print("Done")

def intersect(vid):

    ret = np.load("middleman/Calibration/camera2_params/ret.npy")
    mtx = np.load("middleman/Calibration/camera2_params/mtx.npy")
    dist = np.load("middleman/Calibration/camera2_params/dist.npy")
    rvecs = np.load("middleman/Calibration/camera2_params/rvecs.npy")
    tvecs = np.load("middleman/Calibration/camera2_params/tvecs.npy")
    newmtx = np.load("middleman/Calibration/camera2_params/newmtx.npy")

    type = -1
    center_dist = -1

    if vid.isOpened():
        for i in range(0,3):
            ret, img = vid.read()

        og_img = cv2.undistort(img, mtx, dist, None, newmtx)
        cv2.imwrite('og_img.jpg', og_img)

        # Cam 1
        # c = 0.15
        # c_add = 0
        # c_h = 40
        # c_v = 70

        # Cam 2
        c = 0.3
        c_add = 0
        c_h = 50
        c_v = 150

        # # Cam 3
        # c = 0.1
        # c_add = 0
        # c_h = 20
        # c_v = 40

        img = og_img[int(len(og_img)*c + c_add):len(og_img)-c_v, c_h:len(og_img[0])-c_h]      # crop image
        print("og_img dimensions: xLen = ", len(og_img[0]), "\tyLen = ", len(og_img))
        print("img dimensions: xLen = ", len(img[0]), "\tyLen = ", len(img))
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)                 # convert cropped image to grayscale
        og_gray = cv2.cvtColor(og_img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,200,255)                             # edge detection with Canny
        cv2.imwrite('edges.jpg',edges)                              # write edges to image
        lines = cv2.HoughLines(edges,1,np.pi/180,20)                # detect lines

        if lines is not None:
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
            #         cv2.line(img,(x1,y1),(x2,y2),(255,0,0),2)
            # cv2.imwrite('allLines.jpg',img)


            # Extract strong lines
            strong_lines = np.zeros([4,1,2])        # [vert1, vert2, horz1, horz2]

            n2 = 0
            numVert = 0
            numHorz = 0
            for n1 in range(0,len(lines)):
                for rho,theta in lines[n1]:
                    if n1 == 0:
                        if math.tan(theta) != 0 and abs(-1/math.tan(theta)) > 1:
                            strong_lines[0] = lines[n1]
                            numVert += 1
                            print("stored vert1")
                        # slope not vertical and |slope|<0.5 and
                        elif math.tan(theta) != 0 and abs(1/math.tan(theta)) < 0.5:
                            y_center = -1/math.tan(theta)*(int(len(img[0])/2) - np.cos(theta)*rho) + np.sin(theta)*rho
                            print("y coordinate at x = ", int(len(img[0])/2), ": ", y_center)
                            cv2.circle(og_img,(int(len(img[0])/2) + c_h,int(y_center) + int(len(og_img)*c + c_add)),radius=1,color=(0,255,0),thickness=2)
                            if y_center > 0 and y_center < len(img[0]):
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
                            if math.tan(theta) != 0 and abs(-1/math.tan(theta)) > 1 and numVert < 2:                  # check if pos vertical and no pos vert found
                                x_center = (int(len(img)/2) - np.sin(theta)*rho)/(-1/math.tan(theta)) + np.cos(theta)*rho
                                print("x coordinate at y = ", int(len(img)/2), ": ", x_center)
                                if x_center > 0 and x_center < len(img):
                                    if numVert > 0:
                                        if abs(x_center - ((int(len(img)/2) - np.sin(strong_lines[0][0][1])*strong_lines[0][0][0])/(-1/math.tan(strong_lines[0][0][1])) + np.cos(strong_lines[0][0][1])*strong_lines[0][0][0])) > 10:
                                            strong_lines[numVert] = lines[n1]
                                            numVert += 1
                                            n2 += 1
                                            print("stored vert2")
                                    else:
                                        strong_lines[0] = lines[n1]
                                        numVert += 1
                                        n2 += 1
                                        print("stored vert1")
                            elif math.tan(theta) != 0 and abs(1/math.tan(theta)) < 0.5 and numHorz < 2:                # check if horiz line and < 2 strong horizs
                                #strong_lines = np.concatenate((strong_lines, [lines[n1]]), axis=0)
                                y_center = -1/math.tan(theta)*(int(len(img[0])/2) - np.cos(theta)*rho) + np.sin(theta)*rho
                                print("y coordinate at x = ", int(len(img[0])/2), ": ", y_center)
                                cv2.circle(og_img,(int(len(img[0])/2) + c_h,int(y_center) + int(len(og_img)*c + c_add)),radius=1,color=(0,255,0),thickness=2)
                                if y_center > 0 and y_center < len(img[0]):
                                    if numHorz > 0:
                                        # Check for gap between potential horizontal and existing horizontal
                                        if abs(y_center - (-1/math.tan(strong_lines[2][0][1])*(int(len(img[0])/2) - np.cos(strong_lines[2][0][1])*strong_lines[2][0][0]) + np.sin(strong_lines[2][0][1])*strong_lines[2][0][0])) > 10:
                                            strong_lines[2 + numHorz] = lines[n1]
                                            numHorz += 1
                                            n2 += 1
                                    else:
                                        strong_lines[2 + numHorz] = lines[n1]
                                        numHorz += 1
                                        n2 += 1

            print("numHorz = ", numHorz)

            # print("strong lines before deletion: ")
            # print(strong_lines)
            # print(strong_lines.shape)


            if numVert > 1:
                # Remove unnecessary array elements
                if numHorz < 2:
                    for n in range(numHorz + 2, 4):
                        #print("deleting n = ", 5-n)
                        strong_lines = np.delete(strong_lines, len(strong_lines)-1, 0)

                print("strong lines after deletion: ")
                print(strong_lines)

                # Display strong lines
                i = 0
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
                        cv2.line(img,(x1,y1),(x2,y2),(10+80*i,0,0),2)
                        i += 1
                # cv2.imwrite('strongLines.jpg',img)
                # im = Image.open('strongLines.jpg')
                # im.show()


                # Calculate center line (unnecessary atm)
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
                # if c_line_x1 != c_line_x2 :
                #     cSlope = (c_line_y2 - c_line_y1)/(c_line_x2 - c_line_x1)
                # else :
                #     cSlope =


                # Calculate center point
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

                print("centerX = ", centerX, "\txDim = ", len(img[0]))
                print("centerY = ", centerY, "\tyDim = ", len(img))
                # center_dist = 13*math.pow(1.03,-0.2*centerY) + 8           # distance eq for cam 1, mouse C
                center_dist = 13*math.pow(1.05,-0.1*centerY) + 7           # distance eq for cam 3, mouse D
                # center_dist = 16*math.pow(1.07,-0.1*centerY) + 4            # distance eq for cam 2, mouse G
                print("distance to intersection: ", center_dist)
                cv2.circle(img,(centerX,centerY),radius=1,color=(0,255,0),thickness=2)
                cv2.imwrite('samplePoints.jpg', img)
                cv2.circle(og_img,(centerX + c_h,centerY + int(len(og_img)*c + c_add)),radius=1,color=(0,255,0),thickness=2)


                left = 0
                right = 0
                up = 0
                down = 0

                # Check left of center
                centerL = centerX - 90
                cv2.circle(og_img,(centerL + c_h,centerY + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
                if og_gray[centerY + int(len(og_img)*c) + c_add][centerL + c_h] > 200 :
                    left = 1
                # cv2.imwrite('og_samplePoints.jpg',og_img)

                # Check right of center
                centerR = centerX + 90
                cv2.circle(og_img,(centerR + c_h,centerY + int(len(og_img)*c)),radius=1,color=(0,0,100),thickness=2)
                if og_gray[centerY + int(len(og_img)*c) + c_add][centerR + c_h] > 200 :
                    right = 1
                # cv2.imwrite('og_samplePoints.jpg',og_img)

                # Check 20mm above center
                # deltaU = int(math.log(1/60 + math.pow(2.8,-0.02*centerY),2.8)/-0.02)       # calculate pixel difference
                # if deltaU == 0 :
                #     deltaU = 15
                # print("deltaU = ", deltaU)
                # deltaU = 70     # deltaU for cam3
                # deltaU = int(math.log(2/13 + math.pow(1.03,-0.2*centerY),1.03)/-0.2)     # deltaU for cam1
                deltaU = 70
                print("deltaU = ", deltaU)
                centerU = centerY - deltaU
                if centerU < 0:
                    centerU = 0
                cv2.circle(og_img,(centerX + c_h,centerU + int(len(og_img)*c)),radius=1,color=(0,0,255),thickness=2)
                if og_gray[centerU + int(len(og_img)*c) + c_add][centerX + c_h] > 200 :
                    up = 1
                # cv2.imwrite('og_samplePoints.jpg',og_img)

                # Check 20mm below center
                # deltaD = int(math.log(math.pow(2.8,-0.02*centerY) - 1/60,2.8)/-0.02)        # calculate pixel difference
                # if deltaD == 0 :
                #     deltaD = 15
                # print("deltaD = ", deltaD)
                # deltaD = 80     # deltaU for cam3
                # deltaD = int(math.log(math.pow(1.03,-0.2*centerY) - 2/13,1.03)/-0.2)    # deltaD for cam1
                deltaD = 100
                print("deltaD = ", deltaD)
                centerD = centerY + deltaD
                if centerD >= len(img):
                    centerD = len(img) - 1
                # print("centerX + c_h: ", centerX + c_h, "\tcenterD+adj: ", centerD + int(len(og_img)*c))
                cv2.circle(og_img,(centerX + c_h,centerD + int(len(og_img)*c)),radius=1,color=(255,255,0),thickness=2)
                if og_gray[centerD + int(len(og_img)*c) + c_add][centerX + c_h] > 200 :
                    down = 1

                print("samplePoints:")
                print("center: ", og_gray[centerY + int(len(og_img)*c) + c_add][centerX + c_h] > 200)
                print("up: ", og_gray[centerU + int(len(og_img)*c) + c_add][centerX + c_h] > 200)
                print("down: ", og_gray[centerD + int(len(og_img)*c) + c_add][centerX + c_h] > 200)
                print("left: ", og_gray[centerY + int(len(og_img)*c) + c_add][centerL + c_h] > 200)
                print("right: ", og_gray[centerY + int(len(og_img)*c) + c_add][centerR + c_h] > 200)
                print("up left: ", og_gray[centerU + int(len(og_img)*c) + c_add][centerL + c_h] > 200)
                print("up right: ", og_gray[centerU + int(len(og_img)*c) + c_add][centerR + c_h] > 200)
                print("down left: ", og_gray[centerD + int(len(og_img)*c) + c_add][centerL + c_h] > 200)
                print("down right: ", og_gray[centerD + int(len(og_img)*c) + c_add][centerR + c_h] > 200)

                # cv2.imwrite('samplePoints.jpg',img)
                cv2.imwrite('og_samplePoints.jpg',og_img)
                print("left, right, up, down: ", left, ", ", right, ", ", up, ", ", down)


                # Display intersection type
                binary = 8*left + 4*right + 2*up + down
                print("binary = ", binary)
                print()
                if og_gray[centerU + int(len(og_img)*c)][centerL + c_h] > 200 or og_gray[centerU + int(len(og_img)*c)][centerR + c_h] > 200 or og_gray[centerD + int(len(og_img)*c)][centerL + c_h] > 200 or og_gray[centerD + int(len(og_img)*c)][centerR + c_h] > 200:
                    type = 8
                    print("MAZE END")
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
            else:
                print("No path detected")

    return [type, int(center_dist)]

# v = initialize()
# print("start 1")
# arr = intersect(v)
# print("\n\ntype1 = ", arr[0], " at ", arr[1], " cm")
# print("start 2")
# t = intersect(v)
# print("\n\ntype2 = ", t)
# close(v)
