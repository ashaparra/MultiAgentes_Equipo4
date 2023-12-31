from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import requests


class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("./city_files/mapDictionary.json"))

        self.traffic_lights = []
        self.destinations=[]
        self.active_agents = 0
        self.cars_added = 0 


        # Load the map file. The map file is a text file where each character represents an agent.
        with open('./city_files/2023_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    
                    elif col in ["d", "u", "r", "l"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "d" or col =="u" else True, dataDictionary[col], 7 if (col == "d" or col =="u") else 15)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destinations.append(agent.pos)
        # Create the cars
        self.num_agents = N
        self.step_last_car = 0
        self.spawn_cars()               
        self.running = True
        
    # Function to spawn cars every n steps
    def spawn_cars(self):
        # Spawn cars only every n steps
        if self.step_last_car % 10 == 0:
            positions = [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]
            self.cars_added = 0  # Counter for the number of cars added in this cycle

            for pos in positions:
                destination = random.choice(self.destinations)
                
                # Check if the selected cell is already occupied by a car agent
                if not any(isinstance(agent, Car) for agent in self.grid.get_cell_list_contents([pos])):
                    patience = 1
                    agent = Car(f"c_{self.num_agents}", self, destination, 1)
                    self.active_agents += 1
                    self.grid.place_agent(agent, pos)
                    self.schedule.add(agent)
                    self.num_agents += 1
                    self.cars_added += 1

        self.step_last_car += 1

    # Create a function to send the data to the server
    def send_data(self):
        # Define the URL and data
        arrived= self.num_agents - self.active_agents
        url = 'http://52.1.3.19:8585/api/attempts'
        data = {
            "year": 2023,
            "classroom": 301,
            "name": "Equipo 4: Nath y Asha",
            "num_cars": arrived  # Assuming you want to send the number of cars
        }

        # Send the POST request
        response = requests.post(url, json=data)

        if response.ok:
            print('Data sent successfully')
        else:
            print('Failed to send data:', response.text)


        
    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.spawn_cars()
        print("cars created: ", self.num_agents)
        print("cars that arrived: ", self.num_agents - self.active_agents)
        carposition = []
        # Check for crashes -> end simulation
        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid.get_cell_list_contents([(x, y)])
                if any(isinstance(content, Car) for content in cell):
                    carposition.append((x, y))
                    if len(carposition) > 1:
                        print("CRASH")
                        self.running = False
                        return
                carposition.clear()
        print("step:" ,self.schedule.steps)
        # Send data every 100 steps
        if self.schedule.steps % 100 == 0:
            self.send_data()
        if self.cars_added == 0:
            print("NO MORE SPACE")
            print("cars created: ", self.num_agents)
            print("cars that arrived: ", self.num_agents - self.active_agents)
            print("percentage of cars that arrived: ", (self.num_agents - self.active_agents)/self.num_agents)
            self.running = False
        # After reaching 1000 steps, stop the simulation
        if self.step_last_car > 1000:
            print("TIMEOUT")
            print("cars created: ", self.num_agents)
            print("cars that arrived: ", self.num_agents - self.active_agents)
            print("percentage of cars that arrived: ", (self.num_agents - self.active_agents)/self.num_agents)
            self.running = False