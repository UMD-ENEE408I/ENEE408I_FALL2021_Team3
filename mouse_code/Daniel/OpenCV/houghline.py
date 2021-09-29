import cv2
import numpy as np
  
vid = cv2.VideoCapture(1)
  
while(vid.isOpened()):
      

    ret, img = vid.read()

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('road_grayscale.jpg',gray)
    edges = cv2.Canny(gray,50,150)
    cv2.imshow('edges', edges)

    
    # cv2.imwrite('road_edges.jpg',edges)

    minLineLength = 100
    maxLineGap = 10
    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)
    print(lines)
    if not lines is None:
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

    cv2.imshow('houghlines5.jpg',img) 

    # cv2.imshow('frame', frame)
      
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  

vid.release()
cv2.destroyAllWindows()