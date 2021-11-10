import requests
from requests.api import get
from dotenv import load_dotenv
import os
import json

load_dotenv()
ROBOT_ID = os.getenv("ROBOT_ID")
LINK = os.getenv("LINK")

def sendCoords(x, y, robotID):
    x = requests.post(LINK + "/coords/" + str(robotID), data={"x": x, "y": y})
    print(x)

def getData():
    ret = requests.get(LINK + "/dumpdata")

    data = ret.json()

def clearData():
    ret = requests.get(LINK + "/clear")

    data = ret.json()

sendCoords(10,20,1)

getData()