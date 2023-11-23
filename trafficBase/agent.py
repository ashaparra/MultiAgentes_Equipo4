from mesa import Agent
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.dijkstra import DijkstraFinder
import random

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
    def create_custom_grid(self):
        """
        Create a directed graph for pathfinding that takes into account the directions of the roads at neighbor cells.
        """
        # Initialize the grid with all cells potentially walkable
        grid = Grid(matrix=[[0 for _ in range(self.model.width)] for _ in range(self.model.height)])

        # Iterate through each cell in the Mesa grid
        for x in range(self.model.width):
            for y in range(self.model.height):
                current_pos = (x, y)
                cell_contents = self.model.grid.get_cell_list_contents(current_pos)
                current_node = grid.node(x, y)

                # Initialize connections for this node
                current_node.connections = []
                #current_node.walkable = True

                # Check for obstacles and set walkable property
                if any(isinstance(content, Obstacle) for content in cell_contents):
                    current_node.walkable = False
                    continue

                # Get valid neighbors 
                current_road = next((content for content in cell_contents if isinstance(content, Road)), None)
                if current_road:
                    valid_neighbors = self.get_valid_neighbors(current_road.direction,x,y,grid)
                
                for neighbor_pos in valid_neighbors:
                    neighbor_x, neighbor_y = neighbor_pos     
                    neighbor_contents = self.model.grid.get_cell_list_contents((neighbor_x, neighbor_y))
                    # Check if the neighbor cell is an obstacle
                    if any(isinstance(content, Obstacle) for content in neighbor_contents):
                        continue  # Skip this neighbor as it's an obstacle
                    # Check the direction of the road at the neighbor cell
                    neighbor_road = next((content for content in neighbor_contents if isinstance(content, Road)), None)
                    current_node.connections.append(grid.node(neighbor_x, neighbor_y))
                    if neighbor_road:
                        # Adjust the logic to check if the neighbor cell's road allows entry from the current cell
                        #print("neighbor_road.direction: ", neighbor_road.direction)
                        if neighbor_road.direction == 'Right' and (x < neighbor_x):
                            current_node.connections.append(grid.node(neighbor_x, neighbor_y))
                        elif neighbor_road.direction == 'Left' and (x > neighbor_x):
                            current_node.connections.append(grid.node(neighbor_x, neighbor_y))
                        elif neighbor_road.direction == 'Up' and (y < neighbor_y):
                            current_node.connections.append(grid.node(neighbor_x, neighbor_y))
                        elif neighbor_road.direction == 'Down' and (y > neighbor_y):
                            current_node.connections.append(grid.node(neighbor_x, neighbor_y))
                    
        return grid

    def get_valid_neighbors(self, direction,x,y, grid):
        valid_neighbors = []
        if direction == "Right":
            if x + 1 < self.model.width:
                valid_neighbors.append(grid.node(x+1, y))  # Right
                if y + 1 < self.model.height:
                    valid_neighbors.append(grid.node(x+1, y-1))  # Diagonal down-right
                if y - 1 >= 0:
                    valid_neighbors.append(grid.node(x+1, y+1))  # Diagonal up-right

        elif direction == "Left":
            if x - 1 >= 0:
                valid_neighbors.append(grid.node(x-1, y))  # Left
                if y + 1 < self.model.height:
                    valid_neighbors.append(grid.node(x-1, y+1))  # Diagonal down-left
                if y - 1 >= 0:
                    valid_neighbors.append(grid.node(x-1, y-1))  # Diagonal up-left

        elif direction == "Up":
            if y + 1 < self.model.height:
                valid_neighbors.append(grid.node(x, y+1))  # Up
                if x + 1 < self.model.width:
                    valid_neighbors.append(grid.node(x+1, y+1))  # Diagonal up-right
                if x - 1 >= 0:
                    valid_neighbors.append(grid.node(x-1, y+1))  # Diagonal up-left

        elif direction == "Down":
            if y - 1 >= 0:
                valid_neighbors.append(grid.node(x, y-1))  # Down
                if x + 1 < self.model.width:
                    valid_neighbors.append(grid.node(x+1, y-1))  # Diagonal down-right
                if x - 1 >= 0:
                    valid_neighbors.append(grid.node(x-1, y-1))  # Diagonal down-left

        return valid_neighbors

    def print_grid_connections(self, grid):
        """
        Print the grid showing the possible connections for each node.
        """
        # Dictionary to represent the direction of connections
        direction_symbols = {
            (1, 0): '→',  # Right
            (-1, 0): '←', # Left
            (0, 1): '↑', # Up
            (0, -1): '↓',  # Down
        }

        for y in range(self.model.height-1, -1, -1):
            row_str = ''
            for x in range(self.model.width):
                node = grid.node(x, y)
                if not node.walkable:
                    row_str += 'X '  # Mark obstacles
                else:
                    connections_str = ''.join([direction_symbols.get((conn.x - x, conn.y - y), '.') for conn in node.connections])
                    row_str += f'{connections_str} ' if connections_str else '. '
            print(row_str)
        return

    def move(self):
        """
        Moves the car towards its destination using A* pathfinding, considering obstacles and road direction.
        """
        # Create a custom grid for this car agent
        custom_grid = self.create_custom_grid()
        self.print_grid_connections(custom_grid)

        # Convert the car's current position to a node on the custom grid
        # Ensure self.pos is a tuple before using it
        if isinstance(self.pos, tuple):
            start_x, start_y = self.pos
        else:
            # If self.pos is not a tuple, extract x, y coordinates from the GridNode
            start_x, start_y = self.pos.x, self.pos.y

        start_node = custom_grid.node(start_x, start_y)
        end_node = custom_grid.node(self.destination[0], self.destination[1])

        # Create an A* pathfinder instance with no diagonal movement
        finder = DijkstraFinder(diagonal_movement=DiagonalMovement.always )

        # Find the path from start to end using the custom grid
        print("Finding path...")
        path, runs = finder.find_path(start_node, end_node, custom_grid)
        print(path)

        # If a path exists, move the car along the path
        if path and len(path) > 1:
            #print(path)
            next_step = path[1]  # Next step should be a tuple (x, y)
            print( "Type:", type(next_step))
            next_step_pos = (next_step.x, next_step.y) 

            traffic_light_contents = self.model.grid.get_cell_list_contents(next_step_pos)
            traffic_light = next((content for content in traffic_light_contents if isinstance(content, Traffic_Light)), None)
            if traffic_light:
                if not traffic_light.state:
                    print("Traffic light is red, waiting...")
                    return
            self.model.grid.move_agent(self, next_step)
            
            # Manually update self.pos to be a tuple
            self.pos = next_step
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
