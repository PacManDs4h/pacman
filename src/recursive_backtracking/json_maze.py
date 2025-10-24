import json
from .test_maze import propConnexite, checkSymmetry


def maze_to_tabjson(maze, width, height):
    # Convertit le labyrinthe en un tableau bidimensionnel de 0 et 1 pour JSON.
    tab = [[0 if maze.get((x, y)) == ' ' else 1 for x in range(width)]
           for y in range(height)]
    return tab


def getJson(maze):
    (nb_cellules_empty, nb_cellules_wall, p) = propConnexite(
        maze.maze, maze.width, maze.height)
    symmetry = checkSymmetry(maze.maze, maze.width, maze.height)
    maze_json = maze_to_tabjson(maze.maze, maze.width, maze.height)
    donnees = {
        "height": maze.height,
        "width": maze.width,
        "p_connexite": p,
        "nb_cellules_vides": nb_cellules_empty,
        "nb_cellules_mur": nb_cellules_wall,
        "nb_cycles": maze.nb_cycles,
        "num_tunnels_wrap": maze.nb_wrap_tunnels,
        "num_tunnels_centre": maze.nb_center_tunnels,
        "symetrie": symmetry,
        "maze": maze_json
    }
    return json.dumps(donnees)
