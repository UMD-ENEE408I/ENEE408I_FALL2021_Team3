from middleman import intersects_pic as cam
from middleman import client
from middleman.RFJetson import RFJetson
import time


if __name__ == '__main__':
    vid = cam.initialize()

    rfJetson = RFJetson("/dev/cu.usbserial-1440")

    time.sleep(10)

    resp = client.resetServer()

    resp = client.startMaze()


    while resp is None:
        resp = client.startMaze()
        time.sleep(10)
    
    time.sleep(5)

    mouseResp = rfJetson.send(resp)

    if mouseResp == (200,200):
        print("mouse responded")


    time.sleep(5)

    while True:
        typeArr = []
        for i in range(0, 4):
            (intersectType, dist) = cam.intersect(vid)
            typeArr.append(intersectType)
            print(intersectType)
        
        intersectType = max(set(typeArr), key=typeArr.count)
        print("AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
        print(intersectType)

        resp = client.sendCoords(intersectType)

        if resp is not None:
            if resp == 2 or resp == 3: #left or right
                mouseResp = rfJetson.send(1)
                time.sleep(5)
                if mouseResp != (200, 200):
                    break
            mouseResp = rfJetson.send(resp)
            time.sleep(5)
            if mouseResp == (200,200):
                print("mouse responded")
        
        time.sleep(2)




    


