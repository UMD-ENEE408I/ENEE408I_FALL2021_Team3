import requests
from requests.api import get
from requests.models import Response
from dotenv import load_dotenv
import os
import json

load_dotenv()
ROBOT_ID = os.getenv("ROBOT_ID")
LINK = os.getenv("LINK")
START_X = os.getenv("START_X")
START_Y = os.getenv("START_Y")
START_DIR = os.getenv("START_DIR")

def resetServer():
    x = requests.post(LINK + "/resetServer", data={"code": "codesonooopsies"})
    print(x.json())

    if "response" in x.json():
        return int(x.json()["response"])
    else:
        return ""

def startMaze():
    x = requests.post(LINK + "/start/" + str(ROBOT_ID), data={"x": START_X, "y": START_Y, "dir": START_DIR})
    print(x.json()) # should be direction command

    if "response" in x.json():
        return int(x.json()["response"])
    else:
        return -1

def sendCoords(nodex, nodey, nodeType):
    if nodeType == 0:
        return 1 # just move forward

    x = requests.post(LINK + "/coords/" + str(ROBOT_ID), data={"nodex": nodex, "nodey": nodey, "type": nodeType})
    print(x.json()) # should be direction command
    
    if "response" in x.json():
        return int(x.json()["response"])
    else:
        return -1
