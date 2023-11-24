from mesa import Agent
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.dijkstra import DijkstraFinder
import random
from pathfinding.core.graph import Graph
from pathfinding.core.node import Node
from pathfinding.core.graph import GraphNode



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
        self.destination = (5,4)
        self.direction = None
 
    # def create_custom_grid(self):
    #     """
    #     Create a directed graph for pathfinding that takes into account the directions of the roads at neighbor cells.
    #     """
    #     # Initialize the grid with all cells potentially walkable
    #     grid = Grid(matrix=[[1 for _ in range(self.model.width)] for _ in range(self.model.height)])

    #     # Iterate through each cell in the Mesa grid
    #     for x in range(self.model.width):
    #         for y in range(self.model.height):
    #             current_pos = (x, y)
    #             cell_contents = self.model.grid.get_cell_list_contents(current_pos)
    #             current_node = grid.node(x, y)

    #             # Initialize connections for this node
    #             current_node.connections = []
    #             current_node.walkable = True

    #             # Check for obstacles and set walkable property
    #             if any(isinstance(content, Obstacle) for content in cell_contents):
    #                 current_node.walkable = False
    #                 continue

    #             # Get neighbors
    #             neighbors = self.model.grid.get_neighborhood(current_pos, moore=True, include_center=False)
    #             for neighbor_pos in neighbors:
    #                 neighbor_x, neighbor_y = neighbor_pos
    #                 neighbor_contents = self.model.grid.get_cell_list_contents((neighbor_x, neighbor_y))

    #                 # Check if the neighbor cell is an obstacle
    #                 # if any(isinstance(content, Obstacle) for content in neighbor_contents):
    #                 #     continue  # Skip this neighbor as it's an obstacle

    #                 # Check the direction of the road at the neighbor cell
    #                 neighbor_road = next((content for content in neighbor_contents if isinstance(content, Road)), None)
    #                 if neighbor_road:
    #                     # Check if the current cell can connect to the neighbor based on the neighbor's road direction
    #                     if neighbor_road.direction == 'Right' and neighbor_x < x:
    #                         current_node.connections.append(grid.node(neighbor_x, neighbor_y))
    #                     elif neighbor_road.direction == 'Left' and neighbor_x > x:
    #                         current_node.connections.append(grid.node(neighbor_x, neighbor_y))
    #                     elif neighbor_road.direction == 'Up' and neighbor_y < y:
    #                         current_node.connections.append(grid.node(neighbor_x, neighbor_y))
    #                     elif neighbor_road.direction == 'Down' and neighbor_y > y:
    #                         current_node.connections.append(grid.node(neighbor_x, neighbor_y))

    #     return grid
    def create_custom_graph(self):
        # Create an empty dictionary to hold nodes, using their position as keys
        nodes = {}
        edges = []

        # Instantiate GraphNode for each cell in the grid and store in the dictionary
        for x in range(self.model.width):
            for y in range(self.model.height):
                cell_contents = self.model.grid.get_cell_list_contents((x, y))
                if any(isinstance(content, Obstacle) for content in cell_contents):
                    continue  # Skip obstacles

                node_id = f"{x},{y}"
                nodes[node_id] = GraphNode(node_id)
                print(f"Node created: {node_id}")

        # Connect GraphNode objects according to valid neighbors and road directions
        for node_id, node in nodes.items():
            x, y = map(int, node_id.split(','))
            cell_contents = self.model.grid.get_cell_list_contents((x, y))
            current_road = next((content for content in cell_contents if isinstance(content, Road)), None)
            if current_road:
                valid_neighbors = self.get_valid_neighbors(current_road.direction, x, y)
                print(f"Valid neighbors for {node_id}: {valid_neighbors}")
                for neighbor_pos in valid_neighbors:
                    neighbor_id = f"{neighbor_pos[0]},{neighbor_pos[1]}"
                    if neighbor_id in nodes:
                        neighbor_contents = self.model.grid.get_cell_list_contents(neighbor_pos)
                        if any(isinstance(content, Obstacle) for content in neighbor_contents):
                            continue  # Skip obstacles
                        neighbor_road = next((content for content in neighbor_contents if isinstance(content, Road)), None)
                        #if any(isinstance(content, Road) for content in neighbor_contents):
                        if neighbor_road and self.is_road_compatible(current_road.direction, neighbor_road.direction, x, y, neighbor_pos[0], neighbor_pos[1]):
                            edges.append((node, nodes[neighbor_id], 1))
                            print(f"Edge created: {node_id} -> {neighbor_id}")
                        
                        
                        #neighbor_road = next((content for content in neighbor_contents if isinstance(content, Road)), None)
                        #if neighbor_road and self.is_road_compatible(current_road.direction, neighbor_road.direction, x, y, neighbor_pos[0], neighbor_pos[1]):
                        #edges.append((node, nodes[neighbor_id], 1))  # Assuming a cost of 1 for each edge
                        

        return Graph(edges=edges, nodes=nodes, bi_directional=False)




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

    def print_grid_connections(self, graph):
        """
        Print the graph showing the possible connections for each node.
        """
        # Dictionary to represent the direction of connections
        direction_symbols = {
            (1, 0): '→',  # Right
            (-1, 0): '←', # Left
            (0, 1): '↑',  # Up
            (0, -1): '↓', # Down
            (1, 1): '↗',  # Diagonal Up-Right
            (-1, 1): '↖', # Diagonal Up-Left
            (1, -1): '↘', # Diagonal Down-Right
            (-1, -1): '↙', # Diagonal Down-Left
        }

        for y in range(self.model.height - 1, -1, -1):
            row_str = ''
            for x in range(self.model.width):
                node = graph.nodes.get((x, y))
                if node:
                    # For each node, check if there's a connection in a specific direction
                    connections_str = ''
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue  # Skip checking the node itself
                            neighbor = graph.nodes.get((x + dx, y + dy))
                            if neighbor and graph.is_connected(node, neighbor):
                                connections_str += direction_symbols.get((dx, dy), '.')
                            else:
                                connections_str += '.'
                    row_str += f'{connections_str} '
                else:
                    row_str += 'X '  # Mark non-existing nodes as obstacles
            print(row_str)
            


    def move(self):
        """
        Moves the car towards its destination using Dijkstra's pathfinding, considering obstacles and road direction.
        """
        # Create a custom graph for this car agent
        custom_graph = self.create_custom_graph()

        # Ensure self.pos is a tuple representing the position of the car
        start_pos = self.pos if isinstance(self.pos, tuple) else (self.pos.x, self.pos.y)

        # Find the start and end nodes in the graph
        start_node = custom_graph.nodes.get(start_pos)
        end_pos = self.destination
        end_node = custom_graph.nodes.get(end_pos)

        if start_node and end_node:
            # Create a Dijkstra pathfinder instance
            finder = DijkstraFinder(diagonal_movement=DiagonalMovement.always)

            # Find the path from start to end using the custom graph
            path, runs = finder.find_path(start_node, end_node, custom_graph)

             #Debug output
            print(f"Path found: {path}")
            print(f"Runs: {runs}")

            # If a path exists, move the car along the path
            if path and len(path) > 1:
                # The next step is the second node in the path, as the first is the start node
                next_node = path[1]
                next_step_pos = (next_node.x, next_node.y)

                # Check for traffic lights at the next step position
                traffic_light_contents = self.model.grid.get_cell_list_contents(next_step_pos)
                traffic_light = next((content for content in traffic_light_contents if isinstance(content, Traffic_Light)), None)

                # Check the state of the traffic light if there is one
                if traffic_light and not traffic_light.state:
                    print("Traffic light is red, waiting...")
                    return  # Do not move if the traffic light is red

                # Move the car to the next step position
                self.model.grid.move_agent(self, next_step_pos)

                # Manually update self.pos to be a tuple after moving
                self.pos = next_step_pos
            else:
                print("No path found or path is too short.")

    def step(self):
            """
            Step function called by the model, used to determine the car's actions.
            """
            self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
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
