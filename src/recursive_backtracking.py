import random
import time

WIDTH = 39  # Width of the maze (must be odd).
HEIGHT = 19  # Height of the maze (must be odd).
assert WIDTH % 2 == 1 and WIDTH >= 3
assert HEIGHT % 2 == 1 and HEIGHT >= 3

# Use these characters for displaying the maze:
EMPTY = ' '
MARK = '@'
WALL = chr(9608)  # Character 9608 is '█'
NORTH, SOUTH, EAST, WEST = 'n', 's', 'e', 'w'


def initialize_maze():
    """Initialize a filled-in maze data structure."""
    maze = {}
    for x in range(WIDTH):
        for y in range(HEIGHT):
            maze[(x, y)] = WALL  # Every space is a wall at first.
    return maze


def printMaze(maze, markX=None, markY=None):
    """Displays the maze data structure in the maze argument. The
    markX and markY arguments are coordinates of the current
    '@' location of the algorithm as it generates the maze."""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if markX == x and markY == y:
                print(MARK, end='')
            else:
                print(maze[(x, y)], end='')
        print()


def visit(x, y, maze, hasVisited):
    """'Carve out' empty spaces in the maze at x, y and then
    recursively move to neighboring unvisited spaces. This
    function backtracks when the mark has reached a dead end."""
    maze[(x, y)] = EMPTY

    while True:
        unvisitedNeighbors = []
        if y > 1 and (x, y - 2) not in hasVisited:
            unvisitedNeighbors.append(NORTH)
        if y < HEIGHT - 2 and (x, y + 2) not in hasVisited:
            unvisitedNeighbors.append(SOUTH)
        if x > 1 and (x - 2, y) not in hasVisited:
            unvisitedNeighbors.append(WEST)
        # Full width, no symmetry limit
        if x < WIDTH - 2 and (x + 2, y) not in hasVisited:
            unvisitedNeighbors.append(EAST)

        if len(unvisitedNeighbors) == 0:
            return
        else:
            nextIntersection = random.choice(unvisitedNeighbors)
            if nextIntersection == NORTH:
                nextX, nextY = x, y - 2
                maze[(x, y - 1)] = EMPTY
            elif nextIntersection == SOUTH:
                nextX, nextY = x, y + 2
                maze[(x, y + 1)] = EMPTY
            elif nextIntersection == WEST:
                nextX, nextY = x - 2, y
                maze[(x - 1, y)] = EMPTY
            elif nextIntersection == EAST:
                nextX, nextY = x + 2, y
                maze[(x + 1, y)] = EMPTY

            hasVisited.append((nextX, nextY))
            visit(nextX, nextY, maze, hasVisited)


def addCycles(maze, numCycles):
    """Add numCycles loops by randomly removing walls."""
    walls = [(x, y) for x in range(WIDTH)
             for y in range(HEIGHT) if maze[(x, y)] == WALL]
    random.shuffle(walls)
    cyclesAdded = 0

    for x, y in walls:
        if cyclesAdded >= numCycles:
            break
        if (x > 0 and x < WIDTH - 1 and maze[(x - 1, y)] == EMPTY and maze[(x + 1, y)] == EMPTY):
            maze[(x, y)] = EMPTY
            cyclesAdded += 1
        elif (y > 0 and y < HEIGHT - 1 and maze[(x, y - 1)] == EMPTY and maze[(x, y + 1)] == EMPTY):
            maze[(x, y)] = EMPTY
            cyclesAdded += 1


def removeDeadEnds(maze):
    """Remove dead-ends by connecting them to adjacent corridors."""
    maxIterations = 100
    iterations = 0
    while iterations < maxIterations:
        deadEnds = []
        for x in range(1, WIDTH - 1):
            for y in range(1, HEIGHT - 1):
                if maze[(x, y)] == EMPTY:
                    wallsAround = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                                      if maze.get((x + dx, y + dy), WALL) == WALL)
                    if wallsAround == 3:
                        deadEnds.append((x, y))

        if not deadEnds:
            break

        x, y = random.choice(deadEnds)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if maze.get((nx, ny), WALL) == WALL and 0 < nx < WIDTH - 1 and 0 < ny < HEIGHT - 1:
                if maze.get((nx + dx, ny + dy), WALL) == EMPTY:
                    maze[(nx, ny)] = EMPTY
                    break
        iterations += 1


def addTunnels(maze, num_tunnels=3):
    """Add multiple wrap-around tunnels at different horizontal levels."""
    possible_y = list(range(1, HEIGHT - 1, 2)
                      )  # Odd positions to align with maze structure
    random.shuffle(possible_y)
    selected_y = possible_y[:min(num_tunnels, len(possible_y))]

    for tunnelY in selected_y:
        maze[(0, tunnelY)] = EMPTY  # Left tunnel entrance
        maze[(WIDTH - 1, tunnelY)] = EMPTY  # Right tunnel entrance
        # Ensure connection to the maze if not already empty
        if maze.get((1, tunnelY), WALL) == WALL:
            maze[(1, tunnelY)] = EMPTY
        if maze.get((WIDTH - 2, tunnelY), WALL) == WALL:
            maze[(WIDTH - 2, tunnelY)] = EMPTY


def generate_maze(seed=None):
    """Generate a Pacman-like maze with optional seed."""
    if seed is None:
        random.seed(time.time())  # Use system time for random seed
    else:
        random.seed(seed)

    maze = initialize_maze()
    hasVisited = [(1, 1)]
    visit(1, 1, maze, hasVisited)
    addCycles(maze, 10)
    removeDeadEnds(maze)
    addTunnels(maze, num_tunnels=3)  # Add 3 tunnels by default
    return maze


# Generate and display a random maze
maze = generate_maze()
printMaze(maze)
