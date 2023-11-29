from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []
        self.destinations=[]

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2023_base.txt') as baseFile:
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
        
        self.num_agents = N
        self.step_last_car = 0
        self.spawn_cars()               
        self.running = True

    def spawn_cars(self):
        if self.step_last_car == 0:
            for i in range(0, 4):
                destination = random.choice(self.destinations)
                positions = [(0, 0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]
                pos = positions[i]

                # Check if the selected cell is already occupied by a car agent
                if not any(isinstance(agent, Car) for agent in self.grid.get_cell_list_contents([pos])):
                    agent = Car(f"c_{self.num_agents}", self, destination)
                    self.grid.place_agent(agent, pos)
                    self.schedule.add(agent)
                    self.num_agents -= 1

        self.step_last_car += 1

        if self.step_last_car >= 3:
            self.step_last_car = 0


        
    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        self.spawn_cars()
        carposition = []
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