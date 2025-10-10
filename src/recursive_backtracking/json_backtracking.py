def maze_to_tabjson(maze, WIDTH, HEIGHT):
    maze_json = {}
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if maze[(x, y)] == ' ':
                maze_json[(x, y)] = 0
            else:
                maze_json[(x, y)] = 1
    return maze_json
