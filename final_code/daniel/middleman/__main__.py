from middleman import intersects_pic as cam
from middleman import client
from middleman.RFJetson import RFJetson
import time


if __name__ == '__main__':
    vid = cam.initialize()

    rfJetson = RFJetson("COM11")

    time.sleep(2)

    resp = client.resetServer()

    resp = client.startMaze()
    
    time.sleep(2)

    mouseResp = rfJetson.send(resp, 15)

    if mouseResp == (200,200):
        print("mouse responded")


    time.sleep(1)

    while True:
        typeArr = []
        typeArrDict = {}
        for i in range(0, 4):
            (intersectType, dist) = cam.intersect(vid)
            typeArr.append(intersectType)
            if intersectType in typeArrDict.keys():
                newdist = (typeArrDict[intersectType] + dist) / 2
                typeArrDict[intersectType] = newdist
            else:
                typeArrDict[intersectType] = dist
            print(intersectType, " ", dist)

        intersectType = max(set(typeArr), key=typeArr.count)
        intersectDist = typeArrDict[intersectType] if intersectType != 0 else 15
        intersectDist = int(intersectDist)
        print("AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
        print(intersectType, " ", dist)

        resp = client.sendCoords(intersectType)

        if resp is not None:
            if resp == 2 or resp == 3: #left or right
                mouseResp = rfJetson.send(1, intersectDist)
                time.sleep(2)
                if mouseResp != (200, 200):
                    break
            mouseResp = rfJetson.send(resp, intersectDist)
            time.sleep(1)
            if mouseResp == (200,200):
                print("mouse responded")
        
        time.sleep(1)
