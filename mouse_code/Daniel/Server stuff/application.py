from flask import Flask, request

# EB looks for an 'application' callable by default.
application = Flask(__name__)

internalData = {1: [], 2: [], 3: []}

@application.route('/')
def printData():

    return internalData

@application.route("/coords/<robot_id>", methods = ['POST'])
def saveCoords(robot_id):
    # get coords in JSON format ex: {'x': 10, 'y': 20}
    data = request.form
    x = data["x"]
    y = data["y"]

    internalData[int(robot_id)].append((x,y))

    return x + " " + y

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()