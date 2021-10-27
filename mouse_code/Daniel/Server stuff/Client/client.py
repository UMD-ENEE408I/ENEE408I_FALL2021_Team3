import requests
from dotenv import load_dotenv
import os

load_dotenv()
ROBOT_ID = os.getenv("ROBOT_ID")
LINK = os.getenv("LINK")

def sendCoords(x, y, robotID):
    x = requests.post(LINK + "/coords/" + str(robotID), data={"x": x, "y": y})
    print(x)

sendCoords(10,20,1)