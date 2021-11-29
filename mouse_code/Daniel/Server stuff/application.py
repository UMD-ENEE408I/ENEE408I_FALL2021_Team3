from flask import Flask, request, Response, render_template
from itertools import count

from werkzeug.wrappers import ETagRequestMixin

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# Direction Constants
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

# Intersection Type Constants
class ImageIntersectionTypes:
    CROSS = 1
    STRAIGHT_T = 2
    RIGHT_T = 3
    LEFT_T = 4
    LEFT_CORNER = 5
    RIGHT_CORNER = 6
    END = 7

class IntersectionTypes:
    CROSS = [1, 1, 1, 1]
    STRAIGHT_T = [0, 1, 1, 1]
    RIGHT_T = [1, 1, 1, 0]
    LEFT_T = [1, 0, 1, 1]
    LEFT_CORNER = [0, 0, 1, 1]
    RIGHT_CORNER = [0, 1, 1, 0]
    END = [0, 0, 1, 0]
    LEFT_END = [0, 0, 0, 1]
    RIGHT_END = [0, 1, 0, 0]
    REVERSE_END = [1, 0, 0, 0]
    REVERSE_T = [1, 1, 0, 1]
    REVERSE_LEFT_CORNER = [1, 0, 0, 1]
    REVERSE_RIGHT_CORNER = [1, 1, 0, 0]
    

# Counter for naming Nodes
counter = count(0)

currentNode = {1: None, 2: None, 3: None}
nodeDict = {}

startCoords = (0,0)

startDict = {1: False, 2: False, 3: False}

class Node:
    def __init__(self, x, y, type):
        self.north = None
        self.east = None
        self.south = None
        self.west = None
        self.x = x
        self.y = y
        self.name = next(counter)
        self.type = type # [N E S W] 0 for walls ex: [0 0 1 1] for a left turn
        # self.verified = False

    def fullyExplored(self):
        if not (self.type[NORTH] == 1 and self.north is not None):
            return False
        if not (self.type[EAST] == 1 and self.east is not None):
            return False
        if not (self.type[SOUTH] == 1 and self.south is not None):
            return False
        if not (self.type[WEST] == 1 and self.west is not None):
            return False

        return True

def createNode(x,y, type):
    if (x,y) in nodeDict.keys():
        return nodeDict[(x,y)]
    else:
        newNode = Node(x,y,type)
        nodeDict[(x,y)] = newNode
        return newNode

def mazeFullyExplored():
    for node in nodeDict:
        if not node.fullyExplored():
            return False
    
    return True

@application.route('/')
def home():

    return {}


@application.route('/initServer', methods = ['POST'])
def initServer():
    data = request.form



@application.route('/start/<robot_id>', methods = ['GET'])
def start(robot_id):
    # get start coords (maze coords not cm)
    # ex: {'x': 0, 'y':0}
    if startDict[robot_id]:
        return {response: "False"}
    node = createNode(data['x'], data['y'])

    currentNode[robot_id] = node

    return {response: "True"}


@application.route("/coords/<robot_id>", methods = ['POST'])
def saveCoords(robot_id):
    # get coords in JSON format; all coords in cm
    # ex: {'x': 10, 'y': 20, 'direction' = 0, 'nodex': 15, 'nodey': 20, 'type': 1]}
    data = request.form
    x = data["x"]
    y = data["y"]
    direction = data["direction"]
    nodex = data["nodex"]
    nodey = data["nodey"]
    type = data["type"]

    nodeType = None

    if direction == NORTH:
        if type == ImageIntersectionTypes.CROSS:
            nodeType = IntersectionTypes.CROSS
        elif type == ImageIntersectionTypes.STRAIGHT_T:
            nodeType = IntersectionTypes.STRAIGHT_T
        elif type == ImageIntersectionTypes.RIGHT_T:
            nodeType = IntersectionTypes.RIGHT_T
        elif type == ImageIntersectionTypes.LEFT_T:
            nodeType = IntersectionTypes.LEFT_T
        elif type == ImageIntersectionTypes.LEFT_CORNER:
            nodeType = IntersectionTypes.LEFT_CORNER
        elif type == ImageIntersectionTypes.RIGHT_CORNER:
            nodeType = IntersectionTypes.RIGHT_CORNER
        elif type == ImageIntersectionTypes.END:
            nodeType = IntersectionTypes.END
    elif direction == EAST:
        if type == ImageIntersectionTypes.CROSS:
            nodeType = IntersectionTypes.CROSS
        elif type == ImageIntersectionTypes.STRAIGHT_T:
            nodeType = IntersectionTypes.LEFT_T
        elif type == ImageIntersectionTypes.RIGHT_T:
            nodeType = IntersectionTypes.STRAIGHT_T
        elif type == ImageIntersectionTypes.LEFT_T:
            nodeType = IntersectionTypes.REVERSE_T
        elif type == ImageIntersectionTypes.LEFT_CORNER:
            nodeType = IntersectionTypes.REVERSE_LEFT_CORNER
        elif type == ImageIntersectionTypes.RIGHT_CORNER:
            nodeType = IntersectionTypes.LEFT_CORNER
        elif type == ImageIntersectionTypes.END:
            nodeType = IntersectionTypes.LEFT_END
    elif direction == SOUTH:
        if type == ImageIntersectionTypes.CROSS:
            nodeType = IntersectionTypes.CROSS
        elif type == ImageIntersectionTypes.STRAIGHT_T:
            nodeType = IntersectionTypes.REVERSE_T
        elif type == ImageIntersectionTypes.RIGHT_T:
            nodeType = IntersectionTypes.LEFT_T
        elif type == ImageIntersectionTypes.LEFT_T:
            nodeType = IntersectionTypes.RIGHT_T
        elif type == ImageIntersectionTypes.LEFT_CORNER:
            nodeType = IntersectionTypes.REVERSE_RIGHT_CORNER
        elif type == ImageIntersectionTypes.RIGHT_CORNER:
            nodeType = IntersectionTypes.REVERSE_LEFT_CORNER
        elif type == ImageIntersectionTypes.END:
            nodeType = IntersectionTypes.REVERSE_END
    elif direction == WEST:
        if type == ImageIntersectionTypes.CROSS:
            nodeType = IntersectionTypes.CROSS
        elif type == ImageIntersectionTypes.STRAIGHT_T:
            nodeType = IntersectionTypes.RIGHT_T
        elif type == ImageIntersectionTypes.RIGHT_T:
            nodeType = IntersectionTypes.REVERSE_T
        elif type == ImageIntersectionTypes.LEFT_T:
            nodeType = IntersectionTypes.STRAIGHT_T
        elif type == ImageIntersectionTypes.LEFT_CORNER:
            nodeType = IntersectionTypes.RIGHT_CORNER
        elif type == ImageIntersectionTypes.RIGHT_CORNER:
            nodeType = IntersectionTypes.REVERSE_RIGHT_CORNER
        elif type == ImageIntersectionTypes.END:
            nodeType = IntersectionTypes.RIGHT_END

    # create new node
    newNode = createNode(nodex, nodey, nodeType)

    # Decision making here
    

    # Return a direction command
    return x + " " + y

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
