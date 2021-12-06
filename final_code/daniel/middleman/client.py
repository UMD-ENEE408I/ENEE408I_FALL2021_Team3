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
        return x.json()["response"]
    else:
        return None

def startMaze():
    x = requests.post(LINK + "/start/" + str(ROBOT_ID), data={"x": START_X, "y": START_Y, "dir": START_DIR})
    print(x.json()) # should be direction command

    if "response" in x.json():
        try:
            int(x.json()["response"])
        except:
            print(x.json())
            print("error")
        return int(x.json()["response"])
    else:
        return None

def sendCoords(nodeType):

    x = requests.post(LINK + "/coords/" + str(ROBOT_ID), data={"type": nodeType})
    print(x.json()) # should be direction command

    
    
    if "response" in x.json():
        cmdList = list(x.json()["response"])
        return [int(cmdList[i]) for i in range(len(cmdList))]
    else:
        return None
