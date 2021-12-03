import requests
from requests.api import get
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

def startMaze():
    x = requests.post(LINK + "/start/" + str(ROBOT_ID), data={"x": START_X, "y": START_Y, "dir": START_DIR})
    print(x.json()) # should be direction command

    # send direction command to Jetson

def sendCoords(nodex, nodey, nodeType):
    x = requests.post(LINK + "/coords/" + str(ROBOT_ID), data={"nodex": nodex, "nodey": nodey, "type": nodeType})
    print(x.json()) # should be direction command

    # send direction command to Jetson
