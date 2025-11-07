import json
from urllib.request import urlopen
import pygame

WIDTH = 19
HEIGHT = 23

NB_CYCLES = 10
NUM_WRAP_TUNNELS = 2
NUM_CENTER_TUNNELS = 5

url = f"https://pacmaz-s1-o.onrender.com/generate?width={WIDTH}&height={HEIGHT}&nb_cycle={NB_CYCLES}&num_tunnels_wrap={NUM_WRAP_TUNNELS}&num_tunnels_centre={NUM_CENTER_TUNNELS}"
response = urlopen(url)
data_json = json.loads(response.read())

# --- Simple pygame viewer + controllable Pacman (grid-based) ---
def main():

    def wrap_coords(x, y):
        # wrap coordinates on torus
        return (x % width, y % height)

    def cell_free(x, y):
        wx, wy = wrap_coords(x, y)
        try:
            return int(maze[wy][wx]) == 0
        except Exception:
            return False
        
    # toroidal difference helper (returns shortest signed distance between a and b on a ring of size wrap)
    def toroidal_delta(a, b, wrap):
        d = a - b
        if d > wrap / 2:
            d -= wrap
        elif d < -wrap / 2:
            d += wrap
        return d
    
    # extract maze from JSON -- expected format: data_json['maze'] is a list of rows with 0=empty, 1=wall
    maze = data_json.get("maze")
    if maze is None:
        raise RuntimeError("Couldn't find maze data in JSON (expected key 'maze')")

    # maze: list of rows (height) each row is list of columns (width)
    height = data_json.get("height")
    width = data_json.get("width")

    # screen_w = 466
    # screen_h = 496

    # CELL_SIZE = min(screen_w // width, screen_h // height)

    MAX_PIX = 800
    CELL_SIZE = max(8, min(32, MAX_PIX // max(1, width), MAX_PIX // max(1, height)))

    screen_w = width * CELL_SIZE
    screen_h = height * CELL_SIZE

    pygame.init()
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Pacman - arrow keys to move")
    clock = pygame.time.Clock()
    # target frames per second (lower => less CPU)
    FPS = 60

    # movement speed (cells per second). Increase to make Pacman faster.
    MOVE_SPEED_CELLS_PER_SEC = 7.0

    # starting grid cell (integer indices) at bottom middle
    pac_x, pac_y = (width // 2 - 2, height - 2)


    # pixel position of Pacman's center (floats for smooth movement)
    pac_px = pac_x * CELL_SIZE + CELL_SIZE / 2
    pac_py = pac_y * CELL_SIZE + CELL_SIZE / 2

    # movement directions: current movement and next desired direction
    current_dir = (0, 0)
    next_dir = (0, 0)
    # pacman = pygame.image.load("sprites/pacman_left.png")
    small_pellet = pygame.image.load("sprites/small_pellet.png")
    big_pellet = pygame.image.load("sprites/big_pellet.png")
    small_pellet = pygame.transform.scale(small_pellet, (CELL_SIZE, CELL_SIZE))
    big_pellet = pygame.transform.scale(big_pellet, (CELL_SIZE, CELL_SIZE))

    pacman = pygame.image.load("sprites/pacman_full.png")
    pacman = pygame.transform.scale(pacman, (CELL_SIZE, CELL_SIZE))
    pacman_right = pygame.image.load("sprites/pacman_right.png")
    pacman_right = pygame.transform.scale(pacman_right, (CELL_SIZE, CELL_SIZE))

    pacman_down = pygame.transform.rotate(pacman_right, 270)
    pacman_left = pygame.transform.rotate(pacman_right, 180)
    pacman_up = pygame.transform.rotate(pacman_right, 90)

    # score and pellets initialization: place a pellet on every empty cell (maze cell == 0)
    score = 0

    pellets = set()
    big_pellets = set()
    for y, row in enumerate(maze):
        for x, v in enumerate(row):
            try:
                val = int(v)
            except Exception:
                val = 1
            if val == 0:
                if x != 0 and x != width - 1 and y != 0 and y != height - 1:
                    pellets.add((x, y))
    # remove pellet at starting position so pacman doesn't immediately eat one here
    pellets.discard((pac_x, pac_y))
    # remove around ghost house 7 * 5
    for gy in range(height // 2 - 2, height // 2 + 3):
        for gx in range(width // 2 - 3, width // 2 + 4):
            pellets.discard((gx, gy))
    # place 4 big pellets near corners
    big_pellet_positions = [(1,1), (1,height-2), (width-2,1), (width-2,height-2)]
    for pos in big_pellet_positions:
        big_pellets.add(pos)
        # remove pellet at big pellet position so pacman doesn't immediately eat one here
        pellets.discard(pos)
    

    # prepare font for score display
    pygame.font.init()
    score_font = pygame.font.SysFont(None, max(18, CELL_SIZE // 2))

    # colors used for background drawing
    wall_color = (34, 49, 184)
    floor_color = (0, 0, 0)

    # create a background Surface with walls/floor drawn once (cheaper than redrawing grid each frame)
    bg = pygame.Surface((screen_w, screen_h))
    bg.fill(floor_color)
    for y, row in enumerate(maze):
        for x, v in enumerate(row):
            try:
                val = int(v)
            except Exception:
                val = 1
            if val == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(bg, wall_color, rect)
    # draw ghost house door on background as it's static
    door_x = width // 2
    door_y = height // 2 - 1
    door_rect = pygame.Rect(door_x * CELL_SIZE, door_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(bg, (252, 181, 255), door_rect)

    # helper to identify ghost-house door cell
    def is_ghost_house_door(x, y):
        wx, wy = wrap_coords(x, y)
        return (wx, wy) == (door_x, door_y)

    # score surface cache to avoid rerendering each frame
    last_score = None
    score_surf = None

    running = True
    while running:
        # dt in seconds since last frame (use FPS cap)
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    next_dir = (0, -1)
                    # pacman = pygame.image.load("pacman_up.png")
                elif event.key == pygame.K_DOWN:
                    next_dir = (0, 1)
                    # pacman = pygame.image.load("pacman_down.png")
                elif event.key == pygame.K_LEFT:
                    next_dir = (-1, 0)
                    # pacman = pygame.image.load("pacman_left.png")
                elif event.key == pygame.K_RIGHT:
                    next_dir = (1, 0)
                    # pacman = pygame.image.load("pacman_right.png")

        # helper to check if a grid cell is free (with wrap-around)

        # compute current integer cell center (in pixels)
        center_x = pac_x * CELL_SIZE + CELL_SIZE / 2
        center_y = pac_y * CELL_SIZE + CELL_SIZE / 2

        # are we exactly (or close enough) at the center of current cell? (use toroidal distance)
        at_center = abs(toroidal_delta(pac_px, center_x, screen_w)) < 1e-6 and abs(toroidal_delta(pac_py, center_y, screen_h)) < 1e-6

        # if at center, we can change direction: prefer next_dir
        if at_center:
            # snap to exact center to avoid float drift
            pac_px = center_x
            pac_py = center_y
            # try to take the player's desired turn first
            if next_dir != (0, 0):
                tx, ty = pac_x + next_dir[0], pac_y + next_dir[1]
                # block entering the ghost house through the door for Pacman
                if cell_free(tx, ty) and not is_ghost_house_door(tx, ty):
                    current_dir = next_dir
                    # pacman = pygame.image.load(f"sprites/pacman_{directions[next_dir]}.png")
                    # pacman = pacman_down or pacman_up or pacman_left or pacman_right
                    pacman = {(0, -1): pacman_up,
                              (0, 1): pacman_down,
                              (-1, 0): pacman_left,
                                (1, 0): pacman_right}[next_dir]
                else:
                    # if desired direction blocked, keep going current_dir if possible
                    cx, cy = pac_x + current_dir[0], pac_y + current_dir[1]
                    # also prevent continuing into the ghost house door
                    if not cell_free(cx, cy) or is_ghost_house_door(cx, cy):
                        current_dir = (0, 0)
            else:
                # no next direction requested: check if current_dir still possible
                cx, cy = pac_x + current_dir[0], pac_y + current_dir[1]
                # also prevent continuing into the ghost house door
                if not cell_free(cx, cy) or is_ghost_house_door(cx, cy):
                    current_dir = (0, 0)

        # move along current_dir if allowed
        if current_dir != (0, 0):
            speed_px = MOVE_SPEED_CELLS_PER_SEC * CELL_SIZE
            # desired movement in pixels this frame
            move_x = current_dir[0] * speed_px * dt
            move_y = current_dir[1] * speed_px * dt

            # compute target cell (wrapped) and its center for the next cell in movement direction
            target_cell_x = (pac_x + current_dir[0]) % width
            target_cell_y = (pac_y + current_dir[1]) % height
            target_cx = target_cell_x * CELL_SIZE + CELL_SIZE / 2
            target_cy = target_cell_y * CELL_SIZE + CELL_SIZE / 2

            # distance remaining to the target center (use toroidal minimal distance)
            dist_x = toroidal_delta(target_cx, pac_px, screen_w)
            dist_y = toroidal_delta(target_cy, pac_py, screen_h)

            # if movement in this frame would overshoot the target center, snap to center and update grid cell
            if (abs(move_x) >= abs(dist_x) and current_dir[0] != 0) or (abs(move_y) >= abs(dist_y) and current_dir[1] != 0):
                # snap to target center (and wrap grid coords)
                pac_px = target_cx % screen_w
                pac_py = target_cy % screen_h
                pac_x = (pac_x + current_dir[0]) % width
                pac_y = (pac_y + current_dir[1]) % height
                # after arriving, allow immediate turn in the same frame on next loop iteration
            else:
                pac_px += move_x
                pac_py += move_y
                # keep pixel position wrapped so drawing stays on-screen
                pac_px %= screen_w
                pac_py %= screen_h
        else:
            # not moving: keep pac centered on its grid cell (avoid drift)
            pac_px = pac_x * CELL_SIZE + CELL_SIZE / 2
            pac_py = pac_y * CELL_SIZE + CELL_SIZE / 2

        # If Pacman is on a pellet, eat it
        if (pac_x, pac_y) in pellets:
            pellets.remove((pac_x, pac_y))
            score += 10
        elif (pac_x, pac_y) in big_pellets:
            big_pellets.remove((pac_x, pac_y))
            score += 50

        # draw background (walls + floor + door) from cached Surface
        screen.blit(bg, (0, 0))

        # draw pellets by iterating only active pellets (cheaper than scanning full grid)
        sp = small_pellet
        bp = big_pellet
        cs = CELL_SIZE
        for (x, y) in pellets:
            rect = pygame.Rect(x * cs, y * cs, cs, cs)
            screen.blit(sp, rect)
        for (x, y) in big_pellets:
            rect = pygame.Rect(x * cs, y * cs, cs, cs)
            screen.blit(bp, rect)

        # draw pacman
        center = (int(pac_px) - CELL_SIZE // 2, int(pac_py) - CELL_SIZE // 2)
        screen.blit(pacman, center)

        # render score only when it changed
        if score != last_score:
            try:
                score_surf = score_font.render(f"Score: {score}", True, (255, 255, 255))
            except Exception:
                score_surf = None
            last_score = score
        if score_surf:
            screen.blit(score_surf, (4, 4))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()