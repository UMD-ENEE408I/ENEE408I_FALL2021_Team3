from flask import Flask, request, Response
from itertools import count

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# Counter for naming Nodes
counter = count(0)

currentNode = {1: None, 2: None, 3: None}
nodeDict = {}

class Node:
    def __init__(self, x, y):
        self.north = None
        self.east = None
        self.south = None
        self.west = None
        self.x = x
        self.y = y
        self.name = next(counter)

def createNode(x,y):
    if (x,y) in nodeDict.keys():
        return nodeDict[(x,y)]
    else:
        newNode = Node(x,y)
        nodeDict[(x,y)] = newNode
        return newNode


@application.route('/')
def printData():

    return internalData

@application.route('/start/<robot_id>', methods = ['POST'])
def start(robot_id):
    # get start coords (maze coords not cm)
    # ex: {'x': 0, 'y':0}
    data = request.form

    node = createNode(data['x'], data['y'])

    currentNode[robot_id] = node

    return Response("", status=202, mimetype='application/json')


@application.route("/coords/<robot_id>", methods = ['POST'])
def saveCoords(robot_id):
    # get coords in JSON format; all coords in cm
    # ex: {'x': 10, 'y': 20, 'nodes': [{'x': 15, 'y': 20}]}
    data = request.form
    x = data["x"]
    y = data["y"]
    nodes = data["nodes"]

    for node in nodes:
        newNode = Node(node['x'], node['y'])
        

    internalData[int(robot_id)].append((x,y))

    return x + " " + y

@application.route("/dumpdata", methods = ["GET"])
def dumpData():
    return internalData

@application.route("/clear")
def clearData():
    internalData = {1: [], 2: [], 3: []}

    return internalData

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()