from middleman import intersects_pic as cam
from middleman import client
from middleman.RFJetson import RFJetson
import time


if __name__ == '__main__':
    vid = cam.initialize()

    rfJetson = RFJetson("/dev/cu.usbserial-1440")

    time.sleep(1)

    resp = client.resetServer()

    resp = client.startMaze()
    
    time.sleep(.5)

    mouseResp = rfJetson.send(1, 15)

    while mouseResp [0] < 100:
        print("bad response; waiting 5 seconds")
        time.sleep(5)
        print("sending again")
        mouseResp = rfJetson.send(resp, 15)

    print("mouse responded")


    time.sleep(.5)

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

            for cmd in resp:
                if cmd == 5:
                    mouseResp = rfJetson.send(2, 15)
                    while mouseResp[0] < 100:
                        print("bad response; waiting 5 seconds")
                        time.sleep(5)
                        print("sending again")
                        mouseResp = rfJetson.send(2, 15)
                elif cmd == 6:
                    mouseResp = rfJetson.send(3, 15)
                    while mouseResp[0] < 100:
                        print("bad response; waiting 5 seconds")
                        time.sleep(5)
                        print("sending again")
                        mouseResp = rfJetson.send(3, 15)
                elif cmd == 4:
                    mouseResp = rfJetson.send(2, 15)
                    while mouseResp[0] < 100:
                        print("bad response; waiting 5 seconds")
                        time.sleep(5)
                        print("sending again")
                        mouseResp = rfJetson.send(2, 15)
                    time.sleep(1)
                    mouseResp = rfJetson.send(2,15)
                else:
                    if cmd == 2 or cmd == 3: #left or right
                        try:
                            (intersectType, dist) = cam.intersect(vid)
                            if intersectType == 0:
                                dist = 15
                        except:
                            dist = 15
                        mouseResp = rfJetson.send(1, dist)
                        while mouseResp[0] < 100:
                            print("bad response; waiting 5 seconds")
                            time.sleep(5)
                            print("sending again")
                            mouseResp = rfJetson.send(1, dist)
                        print("mouse responded")
                        time.sleep(1)
                    try:
                        (intersectType, dist) = cam.intersect(vid)
                        print("DISTANCE", dist)
                        if intersectType == 0:
                            dist = 15
                    except:
                        dist = 15
                    mouseResp = rfJetson.send(cmd, dist)
                    while mouseResp[0] < 100:
                        print("bad response; waiting 5 seconds")
                        time.sleep(5)
                        print("sending again")
                        mouseResp = rfJetson.send(cmd, dist)
                        time.sleep(1)
                time.sleep(1)
        
        # time.sleep(.5)
