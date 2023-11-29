from mesa import Agent
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.dijkstra import DijkstraFinder
import random
from pathfinding.core.graph import Graph
from pathfinding.core.node import Node
from pathfinding.core.graph import GraphNode
from pathfinding.finder.a_star import AStarFinder

class Car(Agent):
    # ... (existing __init__ and other methods)
    def __init__(self, unique_id, model, destination):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.visited_cells = []
        self.position_stack = []
        self.steps_taken = 0
        self.destination = destination
        self.direction = None
        self.custom_graph = self.create_custom_graph()
        self.path = []
        self.state = "moving"

    def set_waiting(self):
        self.state = "waiting"
       
    def set_moving(self):
        self.state = "moving"


    def create_custom_graph(self):
        # Create an empty dictionary to hold nodes, using their position as keys
        nodes = {}
        edges = []

        # Instantiate GraphNode for each cell in the grid and store in the dictionary
        for y in range(self.model.height):
            for x in range(self.model.width):
                cell_contents = self.model.grid.get_cell_list_contents((x, y))
                if any(isinstance(content, Obstacle) for content in cell_contents):
                    continue  # Skip obstacles

                node_id = y * self.model.width + x  # Unique ID for each node
                nodes[node_id] = GraphNode(node_id)

        # Connect GraphNode objects according to valid neighbors and road directions
        for node_id, node in nodes.items():
            x = node_id % self.model.width
            y = node_id // self.model.width

            cell_contents = self.model.grid.get_cell_list_contents((x, y))
            current_road = next((content for content in cell_contents if isinstance(content, (Road, Traffic_Light))), None)
            if current_road:
                valid_neighbors = self.get_valid_neighbors(current_road.direction, x, y)
                for neighbor_pos in valid_neighbors:
                    neighbor_id = neighbor_pos[1] * self.model.width + neighbor_pos[0]
                    if neighbor_id in nodes:
                        neighbor_contents = self.model.grid.get_cell_list_contents(neighbor_pos)
                        if any(isinstance(content, Obstacle) for content in neighbor_contents):
                            continue  # Skip obstacles

                        neighbor_road = next((content for content in neighbor_contents if isinstance(content, Road)), None)
                        neighbor_traffic_light = next((content for content in neighbor_contents if isinstance(content, Traffic_Light)), None)
                        neighbor_destination = next((content for content in neighbor_contents if isinstance(content, Destination)), None)

                        # Adjust weight for diagonal moves
                        if self.is_diagonal_move(x, y, neighbor_pos[0], neighbor_pos[1]):
                            weight = 1  # Higher weight for diagonal moves
                        else:
                            weight = 1    # Normal weight for straight moves

                        if neighbor_road and self.is_road_compatible(current_road.direction, neighbor_road.direction, x, y, neighbor_pos[0], neighbor_pos[1]):
                            edges.append((node, nodes[neighbor_id], weight))
                        if neighbor_traffic_light and self.is_road_compatible(current_road.direction, neighbor_traffic_light.direction, x, y, neighbor_pos[0], neighbor_pos[1]):
                            edges.append((node, nodes[neighbor_id], weight))
                        if neighbor_destination:
                            edges.append((node, nodes[neighbor_id], 1))  # Keep weight as 1 for destinations

        return Graph(edges=edges, nodes=nodes, bi_directional=False)


    def is_diagonal_move(self, x1, y1, x2, y2):
        """
        Check if the move from (x1, y1) to (x2, y2) is diagonal.
        """
        return abs(x1 - x2) == 1 and abs(y1 - y2) == 1



    def is_road_compatible(self, current_direction, neighbor_direction, current_x, current_y, neighbor_x, neighbor_y):
        # If the current road goes right, the neighbor must be to the right of the current road
        if current_direction == "Right" and neighbor_x > current_x:
            return True
        # If the current road goes left, the neighbor must be to the left of the current road
        elif current_direction == "Left" and neighbor_x < current_x:
            return True
        # If the current road goes up, the neighbor must be above the current road
        elif current_direction == "Up" and neighbor_y > current_y:
            return True
        # If the current road goes down, the neighbor must be below the current road
        elif current_direction == "Down" and neighbor_y < current_y:
            return True
        # If the directions do not match, return False
        return False


    def get_valid_neighbors(self, direction, x, y):
        valid_neighbors = []
        if direction == "Right":
            if x + 1 < self.model.width:
                valid_neighbors.append((x+1, y))  # Right
                if y + 1 < self.model.height:
                    valid_neighbors.append((x+1, y+1))  # Diagonal up-right
                if y - 1 >= 0:
                    valid_neighbors.append((x+1, y-1))  # Diagonal down-right

        elif direction == "Left":
            if x - 1 >= 0:
                valid_neighbors.append((x-1, y))  # Left
                if y + 1 < self.model.height:
                    valid_neighbors.append((x-1, y+1))  # Diagonal up-left
                if y - 1 >= 0:
                    valid_neighbors.append((x-1, y-1))  # Diagonal down-left

        elif direction == "Up":
            if y + 1 < self.model.height:
                valid_neighbors.append((x, y+1))  # Up
                if x + 1 < self.model.width:
                    valid_neighbors.append((x+1, y+1))  # Diagonal up-right
                if x - 1 >= 0:
                    valid_neighbors.append((x-1, y+1))  # Diagonal up-left

        elif direction == "Down":
            if y - 1 >= 0:
                valid_neighbors.append((x, y-1))  # Down
                if x + 1 < self.model.width:
                    valid_neighbors.append((x+1, y-1))  # Diagonal down-right
                if x - 1 >= 0:
                    valid_neighbors.append((x-1, y-1))  # Diagonal down-left

        return valid_neighbors


    def euclidean_distance(self):
        
        return ((self.pos[0] - self.destination[0])**2 + (self.pos[1] - self.destination[1])**2)**0.5
    
    def getPath(self):
        end_id = self.destination[1] * self.model.width + self.destination[0]
            # print("End id: ", end_id)
        start_node = self.custom_graph.nodes.get(self.pos[1] * self.model.width + self.pos[0])
        end_node = self.custom_graph.nodes.get(end_id)
            
        dfinder = DijkstraFinder(diagonal_movement=DiagonalMovement.always)
        # Find the path from start to end using the custom graph
        path, runs = dfinder.find_path(start_node, end_node, self.custom_graph)
        self.path = path
    
    def move(self):
        """
        Moves the car towards its destination using Dijkstra's pathfinding, considering obstacles and road direction.
        """

        # Create a custom graph for this car agent
        for node in self.custom_graph.nodes.values():
            node.cleanup()
        
        if not self.path:
            self.getPath()
        
        
        # If a path exists, move the car along the path
        if self.path and len(self.path) > 1:
            # The next step is the second node in the path, as the first is the start node
            next_node = self.path[1]

            # Convert the next node's ID to a tuple representing the position of the car
            nx = next_node.node_id % self.model.width
            ny = next_node.node_id // self.model.width
            next_step_pos = (nx, ny)
            self.check_path_recalculation_trigger(next_step_pos)
            car_agent_content = self.model.grid.get_cell_list_contents(next_step_pos)

            if any(isinstance(content, Car) for content in car_agent_content):
                # print("Car in front, waiting...")
                self.set_waiting()
                return

            # Check for traffic lights at the next step position
            traffic_light_contents = self.model.grid.get_cell_list_contents(next_step_pos)
            traffic_light = next((content for content in traffic_light_contents if isinstance(content, Traffic_Light)), None)

            # Check the state of the traffic light if there is one
            if traffic_light and not traffic_light.state:
                # print("Traffic light is red, waiting...")
                self.set_waiting()
                return  # Do not move if the traffic light is red

            # Move the car to the next step position
            self.set_moving()
            self.model.grid.move_agent(self, next_step_pos)
            self.path.pop(0)

            # Manually update self.pos to be a tuple after moving
            self.pos = next_step_pos
        else:
            #self.getPath()
            print("No path found or path is too short.")

    def check_path_recalculation_trigger(self, next_pos):

        next_step_pos = next_pos
        car_agent_content = self.model.grid.get_cell_list_contents(next_step_pos)

        # Check for waiting cars
        waiting_cars = [content for content in car_agent_content if isinstance(content, Car) and content.state == "waiting"]
        if len(waiting_cars) >= 1:
            self.needs_path_recalculation = True
            self.recalculate_path()
        else:
            self.needs_path_recalculation = False
    
    def modify_graph_for_recalculation(self):
        # Remove nodes where waiting cars are located
        for car in self.model.schedule.agents:
            if isinstance(car, Car) and car.state == "waiting":
                node_id = car.pos[1] * self.model.width + car.pos[0]
                if node_id in self.custom_graph.nodes:
                    del self.custom_graph.nodes[node_id]

    def restore_graph(self):
        # Restore the graph to its original state
        self.custom_graph = self.create_custom_graph()
    
    def recalculate_path(self):
        self.modify_graph_for_recalculation()
        self.getPath()  # This will now find a path using the modified graph
        print("recalculated path")
        self.restore_graph()





    def remove_car(self):
        """
        Removes the car from the grid.
        """
        if self.pos[0] == self.destination[0] and self.pos[1] == self.destination[1]:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            # print("Car arrived at destination and was removed from the grid.")

    def step(self):
            """
            Step function called by the model, used to determine the car's actions.
            """
            if self.pos[0] == self.destination[0] and self.pos[1] == self.destination[1]:
                self.remove_car()
            else:
                self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, direction="Rigth" ,timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.direction = direction
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
