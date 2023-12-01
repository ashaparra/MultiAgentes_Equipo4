# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git 

from flask import Flask, request, jsonify
from model import CityModel
from agent import *
import requests
import json

# Size of the board:
number_agents = 4
cityModel = None
currentStep = 0
# Create a Flask application instance
app = Flask("Traffic example")

# Define the endpoint for the POST method
@app.route('/init', methods=['POST'])
def initModel():
    global currentStep, cityModel, number_agents, width, height
    cityModel = CityModel(number_agents)
    return jsonify({"message":"Parameters recieved, model initiated."})

# add a new agent to the model and aelf.num_agents += 1
@app.route('/getAgents', methods=['GET'])
def getAgents():
    global cityModel

#
    if request.method == 'GET':
        agentPositions = [{"id": str(car.unique_id), "x": x, "y":1, "z":z} 
                        #   for x in range (cityModel.width) for z in range (cityModel.height)
                        #   for car in cityModel.grid.get_cell_list_contents((x, z)) if isinstance(car, Car)]
                            for cells, (x,z) in cityModel.grid.coord_iter() 
                            for car in cells if isinstance(car, Car)
                                ]

        return jsonify({'positions':agentPositions})

# Gets the obstacle 
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global cityModel

    # get the obstacles
    if request.method == 'GET':
        obstaclePositions = [{"id": str(obs.unique_id), "x": x, "y":1, "z":z} 
                            for cells, (x,z) in cityModel.grid.coord_iter() 
                            for obs in cells if isinstance(obs, Obstacle)]

        return jsonify({'positions':obstaclePositions})

# Gets the traffic lights 8status)
@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global cityModel

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(tl.unique_id), "x": x, "y":1, "z":z, "state": tl.state,"direction": tl.direction} 
                                for cells, (x,z) in cityModel.grid.coord_iter() 
                                for tl in cells if isinstance(tl, Traffic_Light)]

        return jsonify({'positions':trafficLightPositions})

# Gets the destinations
@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global cityModel
    # get the destinations
    if request.method == 'GET':
        destinationPositions = [{"id": str(d.unique_id), "x": x, "y":1, "z":z} 
                                for cells, (x,z) in cityModel.grid.coord_iter()
                                for d in cells if isinstance(d, Destination)]

        return jsonify({'positions':destinationPositions})
    
# Gets the roads
@app.route('/getRoads', methods=['GET'])
def getRoads():
    global cityModel

    if request.method == 'GET':
        roadPositions = [{"id": str(r.unique_id), "x": x, "y":1, "z":z} 
                        for cells, (x,z) in cityModel.grid.coord_iter() 
                        for r in cells if isinstance(r, Road)]

        return jsonify({'positions':roadPositions})

# Uodates the dato fo our durectuon
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