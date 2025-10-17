def maze_to_tabjson(maze, width, height):
    """Convertit le labyrinthe en un tableau bidimensionnel de 0 et 1 pour JSON."""
    tab = [[0 if maze.get((x, y)) == ' ' else 1 for x in range(width)]
           for y in range(height)]
    return tab
