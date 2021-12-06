from os import linesep
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

class RFDirectionCommands:
    STOP = 0
    FORWARD = 1
    LEFT = 2
    RIGHT = 3
    LEFTLEFT = 4

# Intersection Type Constants
class ImageIntersectionTypes:
    LINE = 0
    CROSS = 1
    STRAIGHT_T = 2
    RIGHT_T = 3
    LEFT_T = 4
    LEFT_CORNER = 5
    RIGHT_CORNER = 6
    END = 7
    MAZE_END = 8
    ERROR = -1

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
    LINE = [0, 0, 0, 0]
    ERROR = None
    
class serverVars:
# Counter for naming Nodes
    counter = count(0)

    currentNode = {'1': None, '2': None, '3': None}
    currentDirection = {'1': None, '2': None, '3': None} # use NESW Constants above
    currentCoords = {'1': (None, None), '2': (None, None), '3': (None, None)}
    nodeDict = {}
    startNode = None
    mazeDimension = 20

mazeExit = (10,10)

class Node:
    def __init__(self, x, y, type):
        self.directions = {NORTH: None, EAST: None, SOUTH: None, WEST: None}
        self.x = x
        self.y = y
        self.name = next(serverVars.counter)
        self.type = type # [N E S W] 0 for walls ex: [0 0 1 1] for a left turn
        # self.verified = False

    def fullyExplored(self):
        print(self.type)
        print(self.directions[EAST])
        if  self.type[NORTH] == 1 and self.directions[NORTH] is None:
            return False
        if  self.type[EAST] == 1 and self.directions[EAST] is None:
            return False
        if  self.type[SOUTH] == 1 and self.directions[SOUTH] is None:
            return False
        if  self.type[WEST] == 1 and self.directions[WEST] is None:
            return False

        return True

def createNode(x,y, type):
    if (x,y) in serverVars.nodeDict.keys():
        return serverVars.nodeDict[(x,y)]
    else:
        newNode = Node(x,y,type)
        serverVars.nodeDict[(x,y)] = newNode
        return newNode

def mazeFullyExplored():
    for node in serverVars.nodeDict.values():
        if not node.fullyExplored():
            break
            return False
    
    return True

# visualize graph
# 3 o 
# 2 |   
# 1 └ ─ ┴
#   1 2 3

def visualizeMaze():

    def nodeUnicode(num):
        retStr = '‌‌ ‌‌ ‌‌ ‌‌ ‌‌ '
        if num == 0:
            retStr = '‌‌‌‌ ‌‌ ‌‌  ‌‌ '
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

    # 0 is space, 1 is o, 2 is -, 3 is |
    arr = [ [0] * serverVars.mazeDimension for i in range(serverVars.mazeDimension)]

    for coords in serverVars.nodeDict.keys():
        x = coords[0]
        y = coords[1]

        node = serverVars.nodeDict[coords]
        
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

        if node.directions[NORTH] is not None:
            newx = node.directions[NORTH].x
            newy = node.directions[NORTH].y

            arr[newx][newy] = nodeMark(node.directions[NORTH])

            i = y + 1

            while i < newy:
                arr[x][i] = 15
                i += 1

        if node.directions[EAST] is not None:
            newx = node.directions[EAST].x
            newy = node.directions[EAST].y

            arr[newx][newy] = nodeMark(node.directions[EAST])

            i = x + 1

            while i < newx:
                arr[i][y] = 14
                i += 1

        if node.directions[SOUTH] is not None:
            newx = node.directions[SOUTH].x
            newy = node.directions[SOUTH].y

            arr[newx][newy] = nodeMark(node.directions[SOUTH])

            i = y - 1

            while newy < i:
                arr[x][i] = 15
                i -= 1

        if node.directions[WEST] is not None:
            newx = node.directions[WEST].x
            newy = node.directions[WEST].y

            arr[newx][newy] = nodeMark(node.directions[WEST])

            i = x - 1

            while newx < i:
                arr[i][y] = 14
                i -= 1
    
    retStr = ""
    for y in range(15, -1, -1):
        line = ""
        for x in range(0, 15):
            line += nodeUnicode(arr[x][y])

        if y < 10:
            line = line + '<br>'
        else:
            line = line + '<br>'

        retStr = retStr + line

    return retStr

#
#
# FLASK STUFF HERE
#
#

@application.route('/')
def home():
    # should return a visualization of the stored maze
    return visualizeMaze()

@application.route('/changeDimensions', methods = ['POST'])
def changeDimensions():
    # {"code": "codesonooopsies", "dim": 16}
    data = request.form

    if data["code"] == "codesonooopsies":
        serverVars.mazeDimension = int(data["dim"])

@application.route('/changeExit', methods = ['POST'])
def changeExit():
    # {"code": "codesonooopsies", "x": 10, "y": 10}
    data = request.form

    if data["code"] == "codesonooopsies":
        serverVars.mazeExit = (int(data["x"]), int(data["y"]))

@application.route('/resetServer', methods = ['POST'])
def resetServer():
    # get in form:
    # {"code": "codesonooopsies"}
    data = request.form

    if data["code"] == "codesonooopsies":
        serverVars.counter = count(0)

        serverVars.currentNode = {1: None, 2: None, 3: None}
        serverVars.currentDirection = {1: None, 2: None, 3: None} # use NESW Constants above
        serverVars.nodeDict = {}
        serverVars.startNode = None
        serverVars.currentCoords = {'1': (None, None), '2': (None, None), '3': (None, None)}
    else:
        return {"response": "reset not done"}
    
    return {"response": "reset complete"}


@application.route('/start/<robot_id>', methods = ['POST'])
def start(robot_id):
    # get start coords (maze coords not cm)
    # ex: {'x': 0, 'y':0, 'dir':0}
    data = request.form

    x = int(data["x"])
    y = int(data["y"])
    dir = int(data["dir"])


    # determine type of starting node
    if dir == NORTH:
        startType = IntersectionTypes.REVERSE_END
    elif dir == EAST:
        startType = IntersectionTypes.RIGHT_END
    elif dir == SOUTH:
        startType = IntersectionTypes.END
    elif dir == WEST:
        startType = IntersectionTypes.LEFT_END
    else:
        # error
        print("ERROR at start()")
        return {}

    startNode = createNode(x, y, startType)

    serverVars.currentNode[robot_id] = startNode
    serverVars.currentDirection[robot_id] = dir
    serverVars.currentCoords[robot_id] = (x, y+1)

    return {"response": RFDirectionCommands.FORWARD} # always start by moving forward


def closestUnexploredNode(node, commandList, dir):

    queue = [(node, commandList, dir)]

    while queue:
        curr, cmdList, currDir = queue.pop()
        # if curr is None:
        #     return None
        if curr.fullyExplored() == False:
            return (cmdList, currDir)
        
        # try left
        newDir = (3 + currDir) % 4
        if curr.directions[newDir] is not None and curr.type[newDir] == 1:
            cmdListCpy = [i for i in cmdList]
            cmdListCpy.append(RFDirectionCommands.LEFT)

            queue.append((curr.directions[newDir], cmdListCpy, newDir))
        
        # try right
        newDir = (1 + currDir) % 4
        if curr.directions[newDir] is not None and curr.type[newDir] == 1:
            cmdListCpy = [i for i in cmdList]
            cmdListCpy.append(RFDirectionCommands.RIGHT)

            queue.append((curr.directions[newDir], cmdListCpy, newDir))
        
        # try forward
        newDir = currDir
        if curr.directions[newDir] is not None and curr.type[newDir] == 1:
            cmdListCpy = [i for i in cmdList]
            cmdListCpy.append(RFDirectionCommands.FORWARD)

            queue.append((curr.directions[newDir], cmdListCpy, newDir))

        # try back
        newDir = (2 + currDir) % 4
        if curr.directions[newDir] is not None and curr.type[newDir] == 1:
            cmdListCpy = [i for i in cmdList]
            if curr.type[(3 + currDir) % 4] == 1:
                # if it has a left do a leftleft
                cmdListCpy.append(RFDirectionCommands.LEFTLEFT)
            else:
                cmdListCpy.append(RFDirectionCommands.LEFT)
            
            queue.append((curr.directions[newDir], cmdListCpy, newDir))

    return None

@application.route("/coords/<robot_id>", methods = ['POST'])
def saveCoords(robot_id):
    # get coords in JSON format; all coords in cm
    # ex: {'x': 10, 'y': 20, 'nodex': 15, 'nodey': 20, 'type': 1]}
    data = request.form
    # x = data["x"]
    # y = data["y"]
    direction = serverVars.currentDirection[robot_id]
    # nodex = int(data["nodex"])
    # nodey = int(data["nodey"])
    nodex = serverVars.currentCoords[robot_id][0]
    nodey = serverVars.currentCoords[robot_id][1]
    type = int(data["type"])

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
        elif type == ImageIntersectionTypes.LINE:
            type = IntersectionTypes.LINE
        else:
            type = IntersectionTypes.ERROR
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
        elif type == ImageIntersectionTypes.LINE:
            type = IntersectionTypes.LINE
        else:
            type = IntersectionTypes.ERROR
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
        elif type == ImageIntersectionTypes.LINE:
            type = IntersectionTypes.LINE
        else:
            type = IntersectionTypes.ERROR
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
        elif type == ImageIntersectionTypes.LINE:
            type = IntersectionTypes.LINE
        else:
            type = IntersectionTypes.ERROR

    if type == IntersectionTypes.LINE:
        (x,y) = serverVars.currentCoords[robot_id]
        if direction == NORTH:
            serverVars.currentCoords[robot_id] = (x, y+1)
        elif direction == EAST:
            serverVars.currentCoords[robot_id] = (x+1, y)
        elif direction == SOUTH:
            serverVars.currentCoords[robot_id] = (x, y-1)
        elif direction == WEST:
            serverVars.currentCoords[robot_id] = (x-1, y)
        
        return {"response": [RFDirectionCommands.FORWARD]}

    # create new node
    newNode = createNode(nodex, nodey, nodeType)

    # attach to the last node
    if direction == NORTH:
        print("north")
        if nodex == serverVars.currentNode[robot_id].x and nodey > serverVars.currentNode[robot_id].y:
            serverVars.currentNode[robot_id].directions[NORTH] = newNode
            newNode.directions[SOUTH] = serverVars.currentNode[robot_id]
            serverVars.currentNode[robot_id] = newNode

            print(serverVars.currentNode[robot_id].x)
            print(serverVars.currentNode[robot_id].y)
            if serverVars.currentNode[robot_id].directions[SOUTH] is not None:
                print(serverVars.currentNode[robot_id].directions[SOUTH].x)
                print(serverVars.currentNode[robot_id].directions[SOUTH].y)
        else:
            #something went wrong didnt go NORTH
            print("error didnt go north")
    elif direction == SOUTH:
        print("south")
        if nodex == serverVars.currentNode[robot_id].x and nodey < serverVars.currentNode[robot_id].y:
            serverVars.currentNode[robot_id].directions[SOUTH] = newNode
            newNode.directions[NORTH] = serverVars.currentNode[robot_id]
            serverVars.currentNode[robot_id] = newNode
        else:
            #something went wrong didnt go SOUTH
            print("error didnt go south")
    elif direction == EAST:
        print("east")
        if nodey == serverVars.currentNode[robot_id].y and nodex > serverVars.currentNode[robot_id].x:
            serverVars.currentNode[robot_id].directions[EAST] = newNode
            newNode.directions[WEST] = serverVars.currentNode[robot_id]
            serverVars.currentNode[robot_id] = newNode

            print(serverVars.currentNode[robot_id].x)
            print(serverVars.currentNode[robot_id].y)
            print(serverVars.currentNode[robot_id])
        else:
            #something went wrong didnt go EAST
            print("error didnt go east")
    elif direction == WEST:
        print("west")
        if nodey == serverVars.currentNode[robot_id].y and nodex < serverVars.currentNode[robot_id].x:
            serverVars.currentNode[robot_id].directions[WEST] = newNode
            newNode.directions[EAST] = serverVars.currentNode[robot_id]
            serverVars.currentNode[robot_id] = newNode

            print(serverVars.currentNode[robot_id].x)
            print(serverVars.currentNode[robot_id].y)
            print(serverVars.currentNode[robot_id].type)
        else:
            #something went wrong didnt go WEST
            print("error didnt go west")

    # Decision making here
    if newNode.fullyExplored():
        # check if its an deadend
        if newNode.type == IntersectionTypes.END or newNode.type == IntersectionTypes.LEFT_END or newNode.type == IntersectionTypes.RIGHT_END or newNode.type == IntersectionTypes.REVERSE_END:
            retDirection = RFDirectionCommands.LEFT
            dir = (direction + 2) % 4
            serverVars.currentDirection[robot_id] = dir
            serverVars.currentNode[robot_id] = newNode.directions[(dir)]
            (x,y) = serverVars.currentCoords[robot_id]
            if dir == NORTH:
                serverVars.currentCoords[robot_id] = (x, y+1)
            elif dir == EAST:
                serverVars.currentCoords[robot_id] = (x+1, y)
            elif dir == SOUTH:
                serverVars.currentCoords[robot_id] = (x, y-1)
            elif dir == WEST:
                serverVars.currentCoords[robot_id] = (x-1, y)
        else:
            # look for the nearest node with unexplored branch
            ret = closestUnexploredNode(newNode, [], serverVars.currentDirection[robot_id])

            if ret is not None:
                cmdList, currDir = ret
                serverVars.currentDirection[robot_id] = currDir
                return  {"response": cmdList}
            else:
                # error can't find nearest node
                print("error finding nearest node")
                return {"response": "error"}

    else:
        dir = (3 + direction) % 4
        
        # try left
        if newNode.directions[dir] is None and newNode.type[dir] == 1:
            retDirection = RFDirectionCommands.LEFT
            serverVars.currentDirection[robot_id] = dir
            (x,y) = serverVars.currentCoords[robot_id]
            if dir == NORTH:
                serverVars.currentCoords[robot_id] = (x, y+1)
            elif dir == EAST:
                serverVars.currentCoords[robot_id] = (x+1, y)
            elif dir == SOUTH:
                serverVars.currentCoords[robot_id] = (x, y-1)
            elif dir == WEST:
                serverVars.currentCoords[robot_id] = (x-1, y)
        else:
            # try right
            print("try right")
            dir = (1 + direction) % 4
            if newNode.directions[dir] is None and newNode.type[dir] == 1:
                retDirection = RFDirectionCommands.RIGHT
                serverVars.currentDirection[robot_id] = dir
                (x,y) = serverVars.currentCoords[robot_id]
                if dir == NORTH:
                    serverVars.currentCoords[robot_id] = (x, y+1)
                elif dir == EAST:
                    serverVars.currentCoords[robot_id] = (x+1, y)
                elif dir == SOUTH:
                    serverVars.currentCoords[robot_id] = (x, y-1)
                elif dir == WEST:
                    serverVars.currentCoords[robot_id] = (x-1, y)
            else:
                # try forward
                dir = direction
                if newNode.directions[dir] is None and newNode.type[dir] == 1:
                    retDirection = RFDirectionCommands.FORWARD
                    serverVars.currentDirection[robot_id] = dir
                    (x,y) = serverVars.currentCoords[robot_id]
                    if dir == NORTH:
                        serverVars.currentCoords[robot_id] = (x, y+1)
                    elif dir == EAST:
                        serverVars.currentCoords[robot_id] = (x+1, y)
                    elif dir == SOUTH:
                        serverVars.currentCoords[robot_id] = (x, y-1)
                    elif dir == WEST:
                        serverVars.currentCoords[robot_id] = (x-1, y)
                else:
                    # deadend should turn 180 degrees
                    print("deadend")
                    retDirection = RFDirectionCommands.LEFT
                    dir = (direction + 2) % 4
                    serverVars.currentDirection[robot_id] = dir
                    serverVars.currentNode[robot_id] = newNode.directions[(dir)]
                    (x,y) = serverVars.currentCoords[robot_id]
                    if dir == NORTH:
                        serverVars.currentCoords[robot_id] = (x, y+1)
                    elif dir == EAST:
                        serverVars.currentCoords[robot_id] = (x+1, y)
                    elif dir == SOUTH:
                        serverVars.currentCoords[robot_id] = (x, y-1)
                    elif dir == WEST:
                        serverVars.currentCoords[robot_id] = (x-1, y)
    
    # Return a direction command
    return {"response": [retDirection]}

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
