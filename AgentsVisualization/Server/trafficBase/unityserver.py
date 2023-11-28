# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git 

from flask import Flask, request, jsonify
from model import CityModel
from agent import *

# Size of the board:
number_agents = 4
cityModel = None
currentStep = 0

app = Flask("Traffic example")

@app.route('/init', methods=['POST'])
def initModel():
    global currentStep, cityModel, number_agents, width, height
    cityModel = CityModel(number_agents)
    return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global cityModel

    if request.method == 'GET':
        agentPositions = [{"id": str(car.unique_id), "x": x, "y":1, "z":z} 
                          for x in range (cityModel.width) for z in range (cityModel.height)
                          for car in cityModel.grid.get_cell_list_contents((x, z)) if isinstance(car, Car)]

        return jsonify({'positions':agentPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global cityModel

    if request.method == 'GET':
        obstaclePositions = [{"id": str(obs.unique_id), "x": x, "y":1, "z":z} 
                            for x in range (cityModel.width) for z in range (cityModel.height)
                            for obs in cityModel.grid.get_cell_list_contents((x, z)) if isinstance(obs, Obstacle)]

        return jsonify({'positions':obstaclePositions})
    
@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global cityModel

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(tl.unique_id), "x": x, "y":1, "z":z} 
                            for x in range (cityModel.width) for z in range (cityModel.height)
                            for tl in cityModel.grid.get_cell_list_contents((x, z)) if isinstance(tl, Traffic_Light)]

        return jsonify({'positions':trafficLightPositions})

@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global cityModel

    if request.method == 'GET':
        destinationPositions = [{"id": str(d.unique_id), "x": x, "y":1, "z":z} 
                            for x in range (cityModel.width) for z in range (cityModel.height)
                            for d in cityModel.grid.get_cell_list_contents((x, z)) if isinstance(d, Destination)]

        return jsonify({'positions':destinationPositions})
    
@app.route('/getRoads', methods=['GET'])
def getRoads():
    global cityModel

    if request.method == 'GET':
        roadPositions = [{"id": str(r.unique_id), "x": x, "y":1, "z":z} 
                            for x in range (cityModel.width) for z in range (cityModel.height)
                            for r in cityModel.grid.get_cell_list_contents((x, z)) if isinstance(r, Road)]

        return jsonify({'positions':roadPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, cityModel
    if request.method == 'GET':
        if cityModel == None:
            return jsonify({'message':f'Model not initialized.'})
        cityModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)