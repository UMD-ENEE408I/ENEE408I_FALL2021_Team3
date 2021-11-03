import cv2
import numpy as np
import math

vid = cv2.VideoCapture(1)

ret = np.load("../../Caitlin/OpenCV/Calibration/camera_params/ret.npy")
mtx = np.load("../../Caitlin/OpenCV/Calibration/camera_params/mtx.npy")
dist = np.load("../../Caitlin/OpenCV/Calibration/camera_params/dist.npy")
rvecs = np.load("../../Caitlin/OpenCV/Calibration/camera_params/rvecs.npy")
tvecs = np.load("../../Caitlin/OpenCV/Calibration/camera_params/tvecs.npy")
newmtx = np.load("../../Caitlin/OpenCV/Calibration/camera_params/newmtx.npy")

while(vid.isOpened()):

    ret, img = vid.read()

    img = cv2.undistort(img, mtx, dist, None, newmtx)

    img = img[int(len(img)/2):len(img), 10:len(img[0])-10]


    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,200,255)
    cv2.imwrite('edges.jpg',edges)
    lines = cv2.HoughLines(edges,1,np.pi/180,50)
    print("All lines: ")
    print(lines)


    if not lines is None:
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
                #cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

        # find most vertical edges (main path edges) and most horizontal edges (intersection edges)
        # ind stands for array index
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

        intLines = 0    # =0 if no intersecting lines

        if n > 1:       # there are at least 2 potential intersection lines
            print("There are intersecting lines")

            zeroSlope = 100
            zeroSlope_ind = -1
            i = 0
            for line in lines:
                for rho,theta in line:
                    if theta != 0:
                        slope =  -1/math.tan(theta)

                        # find x and y from rho and theta
                        x0 = rho * math.cos(theta)
                        y0 = rho * math.sin(theta)

                        print("x0 = ", x0, ", y0 = ", y0)

                        if abs(slope)<abs(zeroSlope):
                            if y0 < len(img) - 35:
                                zeroSlope = slope
                                zeroSlope_ind = i
                    i += 1

            zeroSlope2 = 1
            zeroSlope2_ind = zeroSlope_ind
            i = 0
            for line in lines:
                for rho,theta in line:
                    if i != zeroSlope_ind:
                        if theta != 0:
                            slope =  -1/math.tan(theta)
                            print("zeroSlope2 = ", zeroSlope2, "\tslope = ", slope)
                            print("\trho = ", rho, "\tzeroSlope rho = ", lines[zeroSlope_ind][0][0])

                            # find x and y from rho and theta
                            x0 = rho * math.cos(theta)
                            y0 = rho * math.sin(theta)

                            print("x0 = ", x0, ", y0 = ", y0)

                            if abs(slope)<abs(zeroSlope2) and abs(rho-lines[zeroSlope_ind][0][0])>3:
                                print("\tintLines=1")
                                if y0 < len(img) - 35:
                                    zeroSlope2 = slope
                                    zeroSlope2_ind = i
                                    intLines = 1    # =1 if intersecting lines present
                    i += 1

            print("zeroSlope: ", zeroSlope, " @ i=", zeroSlope_ind, ", zeroSlope2: ", zeroSlope2, " @ i=", zeroSlope2_ind)

        # Make new array with only steepest and horizontal-est edges
        slopes = [maxSlope, minSlope]
        kept_lines = np.stack((lines[maxSlope_ind], lines[minSlope_ind]))
        print("kept_lines before adding intLines: ")
        print(kept_lines)
        print("\tsize: ", kept_lines.shape)
        print()
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


        # derive vertical centerline
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
                cv2.line(img,(x1,y1),(x2,y2),(0,255,255*i),2)
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

        # Find intersections
        if intLines == 1:
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

            intersects = []
            i = 0
            while i<2:
                j = 2
                while j<4:
                    intersects.append(intersection(kept_lines[i], kept_lines[j]))
                    j = j+1
                i = i+1

            print(intersects)

            k = 0
            for point in intersects:
                for x,y in point:
                    cv2.circle(img,(x,y),radius=1,color=(0,0,255),thickness=2)
                    d = 120*pow(2.5,-0.02*y)+20
                    print("distance to intersect ", k, ": ", d, " mm")
                    k+=1

    cv2.imshow('img', img)
    cv2.waitKey(1)





vid.release()
cv2.destroyAllWindows()
