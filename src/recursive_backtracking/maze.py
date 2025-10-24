import random
import time
from .test_maze import checkSymmetry

# Use these characters for displaying the maze:
EMPTY = ' '
MARK = '@'
WALL = chr(9608)  # Character 9608 is '█'
NORTH, SOUTH, EAST, WEST = 'n', 's', 'e', 'w'


class Maze:
    def __init__(self, width, height, nb_cycles, nb_wrap_tunnels, nb_center_tunnels):
        self.maze = {}
        self.width = width
        self.height = height
        self.nb_cycles = nb_cycles
        self.nb_wrap_tunnels = nb_wrap_tunnels
        self.nb_center_tunnels = nb_center_tunnels

    def initialize_maze(self):
        """Initialize a filled-in maze data structure."""
        self.maze = {}  # Réinitialiser self.maze
        for x in range(self.width):
            for y in range(self.height):
                self.maze[(x, y)] = WALL  # Every space is a wall at first.

    def printMaze(self, markX=None, markY=None):
        """Displays the maze data structure."""
        for y in range(self.height):
            for x in range(self.width):
                if markX == x and markY == y:
                    print(MARK, end='')
                else:
                    print(self.maze[(x, y)], end='')
            print()

    def visit(self, x, y, hasVisited):
        """'Carve out' empty spaces in the maze at x, y and then
        recursively move to neighboring unvisited spaces."""
        self.maze[(x, y)] = EMPTY

        while True:
            unvisitedNeighbors = []
            if y > 1 and (x, y - 2) not in hasVisited:
                unvisitedNeighbors.append(NORTH)
            if y < self.height - 2 and (x, y + 2) not in hasVisited:
                unvisitedNeighbors.append(SOUTH)
            if x > 1 and (x - 2, y) not in hasVisited:
                unvisitedNeighbors.append(WEST)
            if x < self.width // 2 - 2 and (x + 2, y) not in hasVisited:
                unvisitedNeighbors.append(EAST)

            if len(unvisitedNeighbors) == 0:
                return
            else:
                nextIntersection = random.choice(unvisitedNeighbors)
                if nextIntersection == NORTH:
                    nextX, nextY = x, y - 2
                    self.maze[(x, y - 1)] = EMPTY
                elif nextIntersection == SOUTH:
                    nextX, nextY = x, y + 2
                    self.maze[(x, y + 1)] = EMPTY
                elif nextIntersection == WEST:
                    nextX, nextY = x - 2, y
                    self.maze[(x - 1, y)] = EMPTY
                elif nextIntersection == EAST:
                    nextX, nextY = x + 2, y
                    self.maze[(x + 1, y)] = EMPTY

                hasVisited.append((nextX, nextY))
                self.visit(nextX, nextY, hasVisited)

    def mirrorMaze(self):
        """Mirror the left half of the maze to the right to maintain width."""
        half = self.width // 2
        for x in range(half):
            for y in range(self.height):
                self.maze[(self.width - 1 - x, y)] = self.maze[(x, y)]

    def addCycles(self):
        """Add numCycles loops by randomly removing walls in the left half."""
        walls = [(x, y) for x in range(self.width // 2)
                 for y in range(self.height) if self.maze[(x, y)] == WALL]
        random.shuffle(walls)
        cyclesAdded = 0

        for x, y in walls:
            if cyclesAdded >= self.nb_cycles:
                break
            if (x > 0 and x < self.width // 2 - 1 and self.maze[(x - 1, y)] == EMPTY and self.maze[(x + 1, y)] == EMPTY):
                self.maze[(x, y)] = EMPTY
                cyclesAdded += 1
            elif (y > 0 and y < self.height - 1 and self.maze[(x, y - 1)] == EMPTY and self.maze[(x, y + 1)] == EMPTY):
                self.maze[(x, y)] = EMPTY
                cyclesAdded += 1

    def removeDeadEnds(self):
        """Remove dead-ends in the left half by connecting to adjacent corridors."""
        maxIterations = 100
        iterations = 0
        while iterations < maxIterations:
            deadEnds = []
            for x in range(1, self.width // 2):
                for y in range(1, self.height - 1):
                    if self.maze[(x, y)] == EMPTY:
                        wallsAround = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                                          if self.maze.get((x + dx, y + dy), WALL) == WALL)
                        if wallsAround == 3:
                            deadEnds.append((x, y))

            if not deadEnds:
                break

            x, y = random.choice(deadEnds)
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if self.maze.get((nx, ny), WALL) == WALL and 0 < nx < self.width // 2 and 0 < ny < self.height - 1:
                    if self.maze.get((nx + dx, ny + dy), WALL) == EMPTY:
                        self.maze[(nx, ny)] = EMPTY
                        break
            iterations += 1

    def addTunnels(self):
        """Add wrap-around tunnels at borders and independent center tunnels."""
        possible_y = list(range(1, self.height - 1, 2)
                          )  # Odd positions for alignment
        random.shuffle(possible_y)

        # Select y-positions for wrap-around tunnels
        wrap_y = possible_y[:min(self.nb_wrap_tunnels, len(possible_y))]

        # Select different y-positions for center tunnels
        remaining_y = [y for y in possible_y if y not in wrap_y]
        random.shuffle(remaining_y)
        center_y = remaining_y[:min(self.nb_center_tunnels, len(remaining_y))]

        # Add wrap-around tunnels at borders (left half and mirrored)
        for tunnelY in wrap_y:
            self.maze[(0, tunnelY)] = EMPTY
            self.maze[(1, tunnelY)] = EMPTY
            # Right side will be handled by mirrorMaze

        return center_y

    def applyCenterTunnels(self, center_y):
        """Apply center tunnels symmetrically."""
        center_x = self.width // 2
        for tunnelY in center_y:
            self.maze[(center_x, tunnelY)] = EMPTY
            if self.maze.get((center_x - 1, tunnelY), WALL) == WALL:
                self.maze[(center_x - 1, tunnelY)] = EMPTY
            if self.maze.get((center_x + 1, tunnelY), WALL) == WALL:
                self.maze[(center_x + 1, tunnelY)] = EMPTY

    def addHouse(self):
        pattern = [
            "EEEEEEE",
            "EWWEWWE",
            "EWEEEWE",
            "EWWWWWE",
            "EEEEEEE"
        ]
        corner_x = self.width // 2 - 3
        corner_y = self.height // 2 - 2

        for dy, row in enumerate(pattern):
            for dx, cell in enumerate(row):
                self.maze[(corner_x + dx, corner_y + dy)] = WALL if cell == 'W' else EMPTY

    def generate_maze(self, seed=None):
        """Generate a Pacman-like maze with optional seed."""
        if seed is None:
            random.seed(time.time())  # Use system time for random seed
        else:
            random.seed(seed)

        self.initialize_maze()  # Initialize maze correctly
        hasVisited = [(1, 1)]
        self.visit(1, 1, hasVisited)
        self.addCycles()
        self.removeDeadEnds()
        center_y = self.addTunnels()
        self.mirrorMaze()  # Apply symmetry after all modifications
        self.applyCenterTunnels(center_y)  # Add center tunnels symmetrically
        self.addHouse()
        if not checkSymmetry(self.maze, self.width, self.height):
            print("Warning: Maze is not symmetric!")
        else:
            print("Symétrie: OK")
        return self.maze
