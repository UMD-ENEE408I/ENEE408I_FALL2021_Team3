import cv2
import numpy as np
  
vid = cv2.VideoCapture(1)
  
while(vid.isOpened()):
      

    ret, img = vid.read()

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('road_grayscale.jpg',gray)
    ret,thresh2 = cv2.threshold(gray,230,255,cv2.ADAPTIVE_THRESH_MEAN_C)
    edges = cv2.Canny(thresh2,50,230)
    cv2.imshow('thresh', thresh2)
    cv2.imshow('edges', edges)

    
    # cv2.imwrite('road_edges.jpg',edges)

    minLineLength = 100
    maxLineGap = 10
    lines = cv2.HoughLinesP(edges,1,np.pi/180,40,minLineLength=5,maxLineGap=30)
    print(lines)
    if not lines is None:
        for line in lines:
            for x1,y1,x2,y2 in line:
                slope = (y2-y1)/(x2-x1)
                if abs(slope) > 10:
                    print("slope", slope)
                cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

    cv2.imshow('houghlines5.jpg',img) 



    # cv2.imshow('frame', frame)
      
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  

vid.release()
cv2.destroyAllWindows()