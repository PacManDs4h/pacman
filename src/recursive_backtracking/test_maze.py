def checkSymmetry(maze, WIDTH, HEIGHT):
    """Check if the maze is symmetric around the central column."""
    half = WIDTH // 2
    for x in range(half):
        for y in range(HEIGHT):
            if maze[(x, y)] != maze[(WIDTH - 1 - x, y)]:
                print(f"Asymmetry detected at ({x}, {
                      y}) and ({WIDTH - 1 - x}, {y})")
                return False
    return True


def propConnexite(maze, WIDTH, HEIGHT):
    nb_cellules_empty = 0
    nb_cellules_wall = 0
    for x in range(WIDTH):
        for y in range(1, HEIGHT - 1):
            if (maze[(x, y)] == ' '):
                nb_cellules_empty += 1
            else:
                nb_cellules_wall += 1
    return (nb_cellules_empty, nb_cellules_wall, nb_cellules_wall / nb_cellules_empty)
