import random
import time
from test_recursive_backtracking import *
from json_backtracking import *
import json

WIDTH = 39  # Width of the maze (must be odd).
HEIGHT = 19  # Height of the maze (must be odd).
assert WIDTH % 2 == 1 and WIDTH >= 3
assert HEIGHT % 2 == 1 and HEIGHT >= 3
NB_CYCLES = 10
NUM_WRAP_TUNNELS = 2
NUM_CENTER_TUNNELS = 5

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
    """Displays the maze data structure."""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if markX == x and markY == y:
                print(MARK, end='')
            else:
                print(maze[(x, y)], end='')
        print()


def visit(x, y, maze, hasVisited):
    """'Carve out' empty spaces in the maze at x, y and then
    recursively move to neighboring unvisited spaces."""
    maze[(x, y)] = EMPTY

    while True:
        unvisitedNeighbors = []
        if y > 1 and (x, y - 2) not in hasVisited:
            unvisitedNeighbors.append(NORTH)
        if y < HEIGHT - 2 and (x, y + 2) not in hasVisited:
            unvisitedNeighbors.append(SOUTH)
        if x > 1 and (x - 2, y) not in hasVisited:
            unvisitedNeighbors.append(WEST)
        if x < WIDTH // 2 - 2 and (x + 2, y) not in hasVisited:  # Limit to left half
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


def mirrorMaze(maze):
    half = WIDTH // 2
    for x in range(half):
        for y in range(HEIGHT):
            maze[(WIDTH - 1 - x, y)] = maze[(x, y)]


def addCycles(maze, numCycles):
    walls = [(x, y) for x in range(WIDTH // 2)
             for y in range(HEIGHT) if maze[(x, y)] == WALL]
    random.shuffle(walls)
    cyclesAdded = 0

    for x, y in walls:
        if cyclesAdded >= numCycles:
            break
        if (x > 0 and x < WIDTH // 2 - 1 and maze[(x - 1, y)] == EMPTY and maze[(x + 1, y)] == EMPTY):
            maze[(x, y)] = EMPTY
            cyclesAdded += 1
        elif (y > 0 and y < HEIGHT - 1 and maze[(x, y - 1)] == EMPTY and maze[(x, y + 1)] == EMPTY):
            maze[(x, y)] = EMPTY
            cyclesAdded += 1


def removeDeadEnds(maze):
    maxIterations = 100
    iterations = 0
    while iterations < maxIterations:
        deadEnds = []
        for x in range(1, WIDTH // 2):
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
            if maze.get((nx, ny), WALL) == WALL and 0 < nx < WIDTH // 2 and 0 < ny < HEIGHT - 1:
                if maze.get((nx + dx, ny + dy), WALL) == EMPTY:
                    maze[(nx, ny)] = EMPTY
                    break
        iterations += 1


def addTunnels(maze, num_wrap_tunnels=3, num_center_tunnels=3):
    """Add wrap-around tunnels at borders and independent center tunnels."""
    possible_y = list(range(1, HEIGHT - 1, 2))  # Odd positions for alignment
    random.shuffle(possible_y)

    # Select y-positions for wrap-around tunnels
    wrap_y = possible_y[:min(num_wrap_tunnels, len(possible_y))]

    # Select different y-positions for center tunnels
    remaining_y = [y for y in possible_y if y not in wrap_y]
    random.shuffle(remaining_y)
    center_y = remaining_y[:min(num_center_tunnels, len(remaining_y))]

    # Add wrap-around tunnels at borders (left half and mirrored)
    for tunnelY in wrap_y:
        maze[(0, tunnelY)] = EMPTY
        maze[(1, tunnelY)] = EMPTY
        # Right side will be handled by mirrorMaze

    # We store center_y to apply in generate_maze after mirrorMaze
    return center_y


def applyCenterTunnels(maze, center_y):
    """Apply center tunnels symmetrically."""
    center_x = WIDTH // 2
    for tunnelY in center_y:
        maze[(center_x, tunnelY)] = EMPTY
        if maze.get((center_x - 1, tunnelY), WALL) == WALL:
            maze[(center_x - 1, tunnelY)] = EMPTY
        if maze.get((center_x + 1, tunnelY), WALL) == WALL:
            maze[(center_x + 1, tunnelY)] = EMPTY


def generate_maze(seed=None):
    """Generate a Pacman-like maze with optional seed."""
    if seed is None:
        random.seed(time.time())  # Use system time for random seed
    else:
        random.seed(seed)

    maze = initialize_maze()
    hasVisited = [(1, 1)]
    visit(1, 1, maze, hasVisited)
    addCycles(maze, NB_CYCLES)
    removeDeadEnds(maze)
    center_y = addTunnels(maze, NUM_WRAP_TUNNELS, NUM_CENTER_TUNNELS)
    mirrorMaze(maze)  # Apply symmetry after all modifications
    applyCenterTunnels(maze, center_y)  # Add center tunnels symmetrically
    # Verify symmetry (optional, for debugging)
    if not checkSymmetry(maze, WIDTH, HEIGHT):
        print("Warning: Maze is not symmetric!")
    else:
        print("Symétrie: OK")
    return maze


# Generate and display a random maze
maze = generate_maze()
(nb_cellules_empty, nb_cellules_wall, p) = propConnexite(maze, WIDTH, HEIGHT)
print(f"Nombres cellules vides: {nb_cellules_empty}")
print(f"Nombres cellules Mur: {nb_cellules_wall}")
print(f"Proportion connexité principale: {p}")
printMaze(maze)


def getJson():
    maze_json = maze_to_tabjson(maze, WIDTH, HEIGHT)

    donnees = {
        "height": HEIGHT,
        "width": WIDTH,
        "p_connexite": p,
        "nb_cellules_vides": nb_cellules_empty,
        "nb_cellules_mur": nb_cellules_wall,
        "nb_cycles": NB_CYCLES,
        "num_tunnels_wrap": NUM_WRAP_TUNNELS,
        "num_tunnels_centre": NUM_CENTER_TUNNELS,
        "maze": maze_json
    }

    Json = json.dumps(donnees)
    return Json
