import json
from urllib.request import urlopen
import pygame

WIDTH = 29
HEIGHT = 31

NB_CYCLES = 10
NUM_WRAP_TUNNELS = 2
NUM_CENTER_TUNNELS = 5

url = f"https://pacmaz-s1-o.onrender.com/generate?width={WIDTH}&height={HEIGHT}&nb_cycle={NB_CYCLES}&num_tunnels_wrap={NUM_WRAP_TUNNELS}&num_tunnels_centre={NUM_CENTER_TUNNELS}"
response = urlopen(url)
data_json = json.loads(response.read())

# --- Simple pygame viewer + controllable Pacman (grid-based) ---
def main():
    # extract maze from JSON -- expected format: data_json['maze'] is a list of rows with 0=empty, 1=wall
    maze = data_json.get("maze")
    if maze is None:
        raise RuntimeError("Couldn't find maze data in JSON (expected key 'maze')")

    # maze: list of rows (height) each row is list of columns (width)
    height = data_json.get("height")
    width = data_json.get("width")

    screen_w = 466
    screen_h = 496

    CELL_SIZE = screen_w // width

    pygame.init()
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Pacman - arrow keys to move")
    clock = pygame.time.Clock()

    # movement speed (cells per second). Increase to make Pacman faster.
    MOVE_SPEED_CELLS_PER_SEC = 15.0

    # starting grid cell (integer indices)
    pac_x, pac_y = (1, 1)

    # pixel position of Pacman's center (floats for smooth movement)
    pac_px = pac_x * CELL_SIZE + CELL_SIZE / 2
    pac_py = pac_y * CELL_SIZE + CELL_SIZE / 2

    # movement directions: current movement and next desired direction
    current_dir = (0, 0)
    next_dir = (0, 0)

    running = True
    while running:
        # dt in seconds since last frame
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    next_dir = (0, -1)
                elif event.key == pygame.K_DOWN:
                    next_dir = (0, 1)
                elif event.key == pygame.K_LEFT:
                    next_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    next_dir = (1, 0)

        # helper to check if a grid cell is free
        def cell_free(x, y):
            if not (0 <= x < width and 0 <= y < height):
                return False
            try:
                return int(maze[y][x]) == 0
            except Exception:
                return False

        # compute current integer cell center
        center_x = pac_x * CELL_SIZE + CELL_SIZE / 2
        center_y = pac_y * CELL_SIZE + CELL_SIZE / 2

        # are we exactly (or close enough) at the center of current cell?
        at_center = abs(pac_px - center_x) < 1e-6 and abs(pac_py - center_y) < 1e-6

        # if at center, we can change direction: prefer next_dir
        if at_center:
            # snap to exact center to avoid float drift
            pac_px = center_x
            pac_py = center_y
            # try to take the player's desired turn first
            if next_dir != (0, 0):
                tx, ty = pac_x + next_dir[0], pac_y + next_dir[1]
                if cell_free(tx, ty):
                    current_dir = next_dir
                else:
                    # if desired direction blocked, keep going current_dir if possible
                    cx, cy = pac_x + current_dir[0], pac_y + current_dir[1]
                    if not cell_free(cx, cy):
                        current_dir = (0, 0)
            else:
                # no next direction requested: check if current_dir still possible
                cx, cy = pac_x + current_dir[0], pac_y + current_dir[1]
                if not cell_free(cx, cy):
                    current_dir = (0, 0)

        # move along current_dir if allowed
        if current_dir != (0, 0):
            speed_px = MOVE_SPEED_CELLS_PER_SEC * CELL_SIZE
            # desired movement in pixels this frame
            move_x = current_dir[0] * speed_px * dt
            move_y = current_dir[1] * speed_px * dt

            # compute target center for the next cell in movement direction
            target_cx = (pac_x + current_dir[0]) * CELL_SIZE + CELL_SIZE / 2
            target_cy = (pac_y + current_dir[1]) * CELL_SIZE + CELL_SIZE / 2

            # distance remaining to the target center
            dist_x = target_cx - pac_px
            dist_y = target_cy - pac_py

            # if movement in this frame would overshoot the target center, snap to center and update grid cell
            if (abs(move_x) >= abs(dist_x) and current_dir[0] != 0) or (abs(move_y) >= abs(dist_y) and current_dir[1] != 0):
                # snap to target center
                pac_px = target_cx
                pac_py = target_cy
                pac_x += current_dir[0]
                pac_y += current_dir[1]
                # after arriving, allow immediate turn in the same frame on next loop iteration
            else:
                pac_px += move_x
                pac_py += move_y
        else:
            # not moving: keep pac centered on its grid cell (avoid drift)
            pac_px = pac_x * CELL_SIZE + CELL_SIZE / 2
            pac_py = pac_y * CELL_SIZE + CELL_SIZE / 2

        # draw
        screen.fill((0, 0, 0))
        wall_color = (34, 49, 184)
        floor_color = (0, 0, 0)
        for y, row in enumerate(maze):
            for x, v in enumerate(row):
                try:
                    val = int(v)
                except Exception:
                    val = 1
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if val == 1:
                    pygame.draw.rect(screen, wall_color, rect)
                else:
                    pygame.draw.rect(screen, floor_color, rect)

        center = (int(pac_px), int(pac_py))
        radius = int(CELL_SIZE * 0.5)
        pygame.draw.circle(screen, (254, 248, 84), center, radius)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()