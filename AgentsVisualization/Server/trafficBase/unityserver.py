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
                        #   for x in range (cityModel.width) for z in range (cityModel.height)
                        #   for car in cityModel.grid.get_cell_list_contents((x, z)) if isinstance(car, Car)]
                            for cells, (x,z) in cityModel.grid.coord_iter() 
                            for car in cells if isinstance(car, Car)
                                ]

        return jsonify({'positions':agentPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global cityModel

    if request.method == 'GET':
        obstaclePositions = [{"id": str(obs.unique_id), "x": x, "y":1, "z":z} 
                            for cells, (x,z) in cityModel.grid.coord_iter() 
                            for obs in cells if isinstance(obs, Obstacle)]

        return jsonify({'positions':obstaclePositions})
    
@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global cityModel

    if request.method == 'GET':
        trafficLightPositions = [{"id": str(tl.unique_id), "x": x, "y":1, "z":z, "state": tl.state,"direction": tl.direction} 
                                for cells, (x,z) in cityModel.grid.coord_iter() 
                                for tl in cells if isinstance(tl, Traffic_Light)]

        return jsonify({'positions':trafficLightPositions})

@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global cityModel

    if request.method == 'GET':
        destinationPositions = [{"id": str(d.unique_id), "x": x, "y":1, "z":z} 
                                for cells, (x,z) in cityModel.grid.coord_iter()
                                for d in cells if isinstance(d, Destination)]

        return jsonify({'positions':destinationPositions})
    
@app.route('/getRoads', methods=['GET'])
def getRoads():
    global cityModel

    if request.method == 'GET':
        roadPositions = [{"id": str(r.unique_id), "x": x, "y":1, "z":z} 
                        for cells, (x,z) in cityModel.grid.coord_iter() 
                        for r in cells if isinstance(r, Road)]

        return jsonify({'positions':roadPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, cityModel
    if request.method == 'GET':
        if cityModel == None:
            return jsonify({'message':f'Model not initialized.'})
        cityModel.step()
        currentStep += 1
        if currentStep % 100 == 0:

            num_cars = get_number_of_active_cars()  # Get the number of active cars
            send_performance_data(num_cars)
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

@app.route('/sendPerformanceData', methods=['GET'])
def send_performance():
    num_cars = get_number_of_active_cars()  # Implement this function to get the number of active cars
    send_performance_data(num_cars)
    return jsonify({'message': 'Performance data sent'})

def send_performance_data(num_cars):
    url = " http://52.1.3.19:8585/api/validate_attempt" 
    data = {
        "year":2023,
        "classroom":301,
        "name": "Equipo4",
        "num_cars": num_cars
        # Add other data if necessary
    }
    headers = {"Content-Type": "application/json"}
    print("Sending data:", data)
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print("Data sent successfully")
        print("Response:", response.json()) 
    else:
        print("Failed to send data")

def get_number_of_active_cars():
        global cityModel
        active_cars = [agent for agent in cityModel.schedule.agents if isinstance(agent, Car)]
        return len(active_cars)


if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)