from mesa import Agent
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
import random


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
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
        self.path = []
        self.road_directions = self.model.road_directions


    def get_neighbors(self, grid, node):
        # Calculate the coordinates of each neighbor and add it to the list if it's on the grid
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = node.x + dx, node.y + dy
            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                neighbor_node = grid.node(nx, ny)
                if neighbor_node.walkable:
                    neighbors.append(neighbor_node)
        return neighbors
    
    def get_directional_path_grid(self):
        # Initialize the grid with walkable nodes
        directional_grid = Grid(matrix=[[1] * self.model.width for _ in range(self.model.height)])

        # Set walkability based on obstacles by checking each cell's contents
        for y in range(self.model.height):
            for x in range(self.model.width):
                cell_contents = self.model.grid.get_cell_list_contents((x, y))
                is_obstacle_here = any(isinstance(obj, Obstacle) for obj in cell_contents)
                directional_grid.node(x, y).walkable = not is_obstacle_here

        # Apply road directions and check for possible turns at intersections
        for (x, y), direction in self.model.road_directions.items():
            node = directional_grid.node(x, y)
            neighbors = self.get_neighbors(directional_grid, node)

            # Set connections based on road directions
            node.connections = []
            for n in neighbors:
                if self.can_move(node, n):  # Only connect nodes if movement is allowed
                    node.connections.append(n)

        return directional_grid

    def at_intersection(self, x, y):
        # Define the relative positions of orthogonal neighbors
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        road_directions = set()

        # Calculate the coordinates of each neighbor
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check if the neighbor is within grid bounds
            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                # If there's a road in that direction, add its direction to the set
                if (nx, ny) in self.road_directions:
                    road_directions.add(self.road_directions[(nx, ny)])

        # If there are more than one direction, it's an intersection
        return len(road_directions) > 1
    
    # def can_move(self, from_node, to_node):
    #     """
    #     Determines if movement from one node to another is allowed based on road direction.
    #     """
    #     from_direction = self.road_directions.get((from_node.x, from_node.y))
    #     to_direction = self.road_directions.get((to_node.x, to_node.y))

    #     # If both nodes have a road direction, ensure the movement is consistent with the direction
    #     if from_direction and to_direction:
    #         if from_direction == '>':
    #             return to_node.x > from_node.x
    #         elif from_direction == '<':
    #             return to_node.x < from_node.x
    #         elif from_direction == '^':
    #             return to_node.y < from_node.y
    #         elif from_direction == 'v':
    #             return to_node.y > from_node.y

    #     # If there's no road direction, or it's an intersection, allow the move
    #     return True
    def can_move(self, from_node, to_node):
        """
        Determines if movement from one node to another is allowed based on road direction.
        """
        from_x, from_y = from_node.pos  # Get the current position
        to_x, to_y = to_node.pos  # Get the target position

        from_direction = self.road_directions.get((from_x, from_y))
        to_direction = self.road_directions.get((to_x, to_y))

        # If both nodes have a road direction, ensure the movement is consistent with the direction
        if from_direction and to_direction:
            if from_direction == '>':
                return to_x > from_x
            elif from_direction == '<':
                return to_x < from_x
            elif from_direction == '^':
                return to_y < from_y
            elif from_direction == 'v':
                return to_y > from_y

        # If there's no road direction, or it's an intersection, allow the move
        return True


    def navigate_to_destination(self):
        # Get a directional grid from the car's local method
        grid = self.get_directional_path_grid()
        start = grid.node(self.pos[0], self.pos[1])
        end = grid.node(self.destination[0], self.destination[1])

        # Use the A* algorithm to find the path
        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, _ = finder.find_path(start, end, grid)

        # If a path is found, convert GridNodes to coordinate tuples and store it for the car to follow
        if path:
            self.path = [(node.x, node.y) for node in path]
            # If you need to exclude the starting point, uncomment the following line:
            self.path = [(node.x, node.y) for node in path[1:]]
        else:
            self.path = []

    # def move(self):
    #     # Move the agent towards the destination if a path exists
    #     if not self.path:
    #         self.navigate_to_destination()

    #     if self.path:
    #         next_position = self.path.pop(0)
            
    #         # Ensure next_position is a tuple, expected by get_cell_list_contents
    #         assert isinstance(next_position, tuple), "next_position must be a tuple of (x, y)"
            
    #         cell_contents = self.model.grid.get_cell_list_contents(next_position)
            
    #         # Check if the next position is a road and if the direction is correct
    #         next_node = None
    #         for content in cell_contents:
    #             if isinstance(content, Road):
    #                 next_node = content
    #                 break

    #         if next_node:
    #             # Check if the current position is a road and get its direction
    #             current_cell_contents = self.model.grid.get_cell_list_contents(self.pos)
    #             current_road = None
    #             for content in current_cell_contents:
    #                 if isinstance(content, Road):
    #                     current_road = content
    #                     break
                    
    #             # If the current position is a road and the direction matches, move the agent
    #             if current_road and current_road.direction == next_node.direction:
    #                 self.model.grid.move_agent(self, next_position)
    #                 self.visited_cells.append(next_position)
    def move(self):
        # Move the agent towards the destination if a path exists
        if not self.path:
            self.navigate_to_destination()

        if self.path:
            next_position = self.path.pop(0)
            
            # Ensure next_position is a tuple, expected by get_cell_list_contents
            assert isinstance(next_position, tuple), "next_position must be a tuple of (x, y)"
            
            cell_contents = self.model.grid.get_cell_list_contents(next_position)
            
            # Check if the next position is a road and if the direction is correct
            next_road_direction = None
            for content in cell_contents:
                if isinstance(content, Road):
                    next_road_direction = content.direction
                    break
                
            # Check if the next step is in the correct direction
            if next_road_direction and self.can_move(self, next_position):
                self.model.grid.move_agent(self, next_position)
                self.visited_cells.append(next_position)




    def step(self):
        """ 
        Determines the new direction it will take, and then moves
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

