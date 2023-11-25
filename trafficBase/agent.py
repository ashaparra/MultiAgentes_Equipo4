from mesa import Agent
import networkx as nx
print("version:",nx.__version__)
import random
class Car(Agent):
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

    # def create_networkx_graph(self):
    #     G = nx.Graph()

    #     # Node creation
    #     for x in range(self.model.width):
    #         for y in range(self.model.height):
    #             cell_contents = self.model.grid.get_cell_list_contents((x, y))
    #             if any(isinstance(content, Obstacle) for content in cell_contents):
    #                 continue  # Skip obstacles
    #             G.add_node((x, y))  # Add nodes representing grid positions

    #     # Edge creation based on road directions and valid neighbors
    #     for node in G.nodes:
    #         x, y = node
    #         cell_contents = self.model.grid.get_cell_list_contents((x, y))
    #         current_road_or_light = next((content for content in cell_contents if isinstance(content, (Road, Traffic_Light))), None)

    #         if current_road_or_light:
    #             # If it's a traffic light, infer direction from adjacent roads
    #             if isinstance(current_road_or_light, Traffic_Light):
    #                 inferred_direction = self.infer_traffic_light_direction(x, y)
    #                 if inferred_direction is None:
    #                     continue  # Skip if no direction can be inferred
    #             else:
    #                 inferred_direction = current_road_or_light.direction

    #             valid_neighbors = self.get_valid_neighbors(inferred_direction, x, y)
    #             for nex, ney in valid_neighbors:
    #                 if (nex, ney) in G.nodes:
    #                     G.add_edge(node, (nex, ney))  # Add edge

    #     return G
    def create_networkx_graph(self):
        G = nx.Graph()

        # Node creation
        for x in range(self.model.width):
            for y in range(self.model.height):
                cell_contents = self.model.grid.get_cell_list_contents((x, y))
                if any(isinstance(content, Obstacle) for content in cell_contents):
                    continue  # Skip obstacles
                G.add_node((x, y))  # Add nodes representing grid positions

        # Edge creation based on road directions and valid neighbors
        for node in G.nodes:
            x, y = node
            cell_contents = self.model.grid.get_cell_list_contents((x, y))
            current_road = next((content for content in cell_contents if isinstance(content, Road)), None)
            if current_road:
                valid_neighbors = self.get_valid_neighbors(current_road.direction, x, y)  # Define valid_neighbors here
                for nex, ney in valid_neighbors:
                    if (nex, ney) in G.nodes:
                        neighbor_road = next((content for content in self.model.grid.get_cell_list_contents((nex, ney)) if isinstance(content, Road)), None)
                        if neighbor_road and self.is_road_compatible(current_road.direction, neighbor_road.direction, x, y, nex, ney):
                            G.add_edge(node, (nex, ney))  # Add edge if neighbor is valid and not an obstacle
                            

        return G

    # def infer_traffic_light_direction(self, x, y):
    #     # Check neighboring roads to infer the direction of the traffic light
    #     directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Up, Right, Down, Left
    #     for dx, dy in directions:
    #         nx, ny = x + dx, y + dy
    #         if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
    #             neighbor_contents = self.model.grid.get_cell_list_contents((nx, ny))
    #             neighbor_road = next((content for content in neighbor_contents if isinstance(content, Road)), None)
    #             if neighbor_road:
    #                 return neighbor_road.direction
    #     return None


    def move(self):
        """
        Moves the car towards its destination using networkx for pathfinding,
        considering obstacles and road direction.
        """
        # Create a custom graph for this car agent using networkx
        custom_graph = self.create_networkx_graph()

        start_node = (self.pos[0], self.pos[1])
        end_node = self.destination
        print(f"Start node: {start_node}, End node: {end_node}")

        if start_node not in custom_graph.nodes or end_node not in custom_graph.nodes:
            print("Start or end node not in graph")
            return

        # Print the graph connections
        self.print_graph_connections(custom_graph)

        # print("Graph nodes:", custom_graph.nodes)
        # print("Graph edges:", custom_graph.edges)
        # print("Graph nodes (first 10):", list(custom_graph.nodes)[None:10:None])
        # print("Graph edges (first 10):", list(custom_graph.edges())[:10])
         


        try:
            # Find the path from start to end using networkx A* pathfinding
            path = nx.astar_path(custom_graph, start_node, end_node, heuristic=self.manhattan_distance)
            print("Path found:", path)

            # The next step is the second node in the path, as the first is the start node
            if len(path) > 1:
                next_step_pos = path[1]

                # Check for traffic lights at the next step position
                traffic_light_contents = self.model.grid.get_cell_list_contents(next_step_pos)
                traffic_light = next((content for content in traffic_light_contents if isinstance(content, Traffic_Light)), None)

                # Check the state of the traffic light if there is one
                if traffic_light and not traffic_light.state:
                    print("Traffic light is red, waiting...")
                    return  # Do not move if the traffic light is red

                # Move the car to the next step position
                self.model.grid.move_agent(self, next_step_pos)
                self.pos = next_step_pos  # Manually update self.pos to be a tuple after moving

        except nx.NetworkXNoPath:
            print("No path found or path is too short.")
    
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

    def euclidean_distance(self, n1, n2):
        x1, y1 = n1
        x2, y2 = n2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def manhattan_distance(self, n1, n2):
        x1, y1 = n1
        x2, y2 = n2
        return abs(x1 - x2) + abs(y1 - y2)


    def step(self):
            """
            Step function called by the model, used to determine the car's actions.
            """
            self.move()
    
    def print_graph_connections(self, G):
        print("Graph Connections:")
        for node in G.nodes:
            neighbors = list(G.neighbors(node))
            print(f"{node}: {neighbors}")

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