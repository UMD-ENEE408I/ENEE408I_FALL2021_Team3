from flask import Flask, request, Response, render_template
from itertools import count
import random

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
currentDirection = {1: None, 2: None, 3: None} # use NESW Constants above
nodeDict = {}

startCoords = (0,0)
mazeExit = (10,10)

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
    for node in nodeDict.values():
        if not node.fullyExplored():
            return False
    
    return True

# visualize graph
# 3 o 
# 2 |   
# 1 └ ─ ┴
#   1 2 3

def visualizeMaze():

    def nodeUnicode(num):
        retStr = ' '
        if num == 0:
            retStr = ' '
        elif num == 1:
            retStr = '┼'
        elif num == 2:
            retStr = '┬'
        elif num == 3:
            retStr = '├'
        elif num == 4:
            retStr = '┤'
        elif num == 5:
            retStr = '┐'
        elif num == 6:
            retStr = '┌'
        elif num == 7:
            retStr = '│'
        elif num == 8:
            retStr = '─'
        elif num == 9:
            retStr = '─'
        elif num == 10:
            retStr = '│'
        elif num == 11:
            retStr = '┴'
        elif num == 12:
            retStr = '┘'
        elif num == 13:
            retStr = '└'
        elif num == 14:
            retStr = '─'
        elif num == 15:
            retStr = '│'

        return retStr



    def nodeMark(node):
        retNum = 0
        if node.type == IntersectionTypes.CROSS:
            retNum = 1
        elif node.type == IntersectionTypes.STRAIGHT_T:
            retNum = 2
        elif node.type == IntersectionTypes.RIGHT_T:
            retNum = 3
        elif node.type == IntersectionTypes.LEFT_T:
            retNum = 4
        elif node.type == IntersectionTypes.LEFT_CORNER:
            retNum = 5
        elif node.type == IntersectionTypes.RIGHT_CORNER:
            retNum = 6
        elif node.type == IntersectionTypes.END:
            retNum = 7
        elif node.type == IntersectionTypes.LEFT_END:
            retNum = 8
        elif node.type == IntersectionTypes.RIGHT_END:
            retNum = 9
        elif node.type == IntersectionTypes.REVERSE_END:
            retNum = 10
        elif node.type == IntersectionTypes.REVERSE_T:
            retNum = 11
        elif node.type == IntersectionTypes.REVERSE_LEFT_CORNER:
            retNum = 12
        elif node.type == IntersectionTypes.REVERSE_RIGHT_CORNER:
            retNum = 13

        return retNum

    mazeDimension = 16

    # 0 is space, 1 is o, 2 is -, 3 is |
    arr = [ [0] * mazeDimension for i in range(mazeDimension)]

    for coords in nodeDict.keys():
        x = coords[0]
        y = coords[1]

        node = nodeDict[coords]
        
        # 1 CROSS
        # 2 STRAIGHT_T
        # 3 RIGHT_T
        # 4 LEFT_T
        # 5 LEFT_CORNER
        # 6 RIGHT_CORNER
        # 7 END
        # 8 LEFT_END
        # 9 RIGHT_END
        # 10 REVERSE_END
        # 11 REVERSE_T
        # 12 REVERSE_LEFT_CORNER
        # 13 REVERSE_RIGHT_CORNER
        # 14 -
        # 15 |

        arr[x][y] = nodeMark(node)

        if node.north is not None:
            newx = node.north.x
            newy = node.north.y

            arr[newx][newy] = nodeMark(node.north)

            i = y + 1

            while i < newy:
                arr[x][i] = 15
                i += 1

        if node.east is not None:
            newx = node.east.x
            newy = node.east.y

            arr[newx][newy] = nodeMark(node.east)

            i = x + 1

            while i < newx:
                arr[x][i] = 14
                i += 1

        if node.south is not None:
            newx = node.south.x
            newy = node.south.y

            arr[newx][newy] = nodeMark(node.south)

            i = y - 1

            while newy < i:
                arr[x][i] = 15
                i -= 1

        if node.west is not None:
            newx = node.west.x
            newy = node.west.y

            arr[newx][newy] = nodeMark(node.west)

            i = x - 1

            while newx < i:
                arr[x][i] = 14
                i -= 1
    
    retStr = ""
    for y in range(15, -1, -1):
        line = ""
        for x in range(0, 15):
            line += nodeUnicode(arr[x][y])

        if y < 10:
            line = str(y + 1)+ '  ' + line + '<br>'
        else:
            line = str(y + 1)+ ' ' + line + '<br>'

        retStr = retStr + line

    return retStr



#
#
# FLASK STUFF HERE
#
#

@application.route('/')
def home():

    return visualizeMaze()


@application.route('/initServer', methods = ['POST'])
def initServer():
    # get in form:
    # {}
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
    if newNode.fullyExplored():
        if 

        if nextDir == 1:


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
