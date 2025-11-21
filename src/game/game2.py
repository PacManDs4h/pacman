import json
from urllib.request import urlopen
import pygame
import spritesheet
import pacman

class Game2:
    def __init__(self, screen):
        self.MAZE_WIDTH = 19
        self.MAZE_HEIGHT = 23
        self.MAZE_NB_CYCLES = 10
        self.MAZE_NUM_WRAP_TUNNELS = 2
        self.MAZE_NUM_CENTER_TUNNELS = 5

        self.MAX_PIX = 800

        self.score = 0
        self.lives = 3

        self.screen = screen
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()

        self.mapImages = []
        self.ghost_door = None
        self.small_pellet = None
        self.big_pellet = None
        self.pacman_sprite = None
        self.pacman_right = None
        self.pacman_left = None
        self.pacman_up = None
        self.pacman_down = None
        self.red_ghost_left = None

        self.bg = None

        self.door_x = 0
        self.door_y = 0


        self.maze = []
        self.height = 0
        self.width = 0
        self.dt = 0
        self.generate_maze()

        self.CELL_SIZE = max(8, min(32, self.MAX_PIX // max(1, self.width), self.MAX_PIX // max(1, self.height)))

        self.load_all_sprites()
        self.pacman = pacman.pacman(self)
        self.generate_pelet()
        self.show_maze()




    # --- Maze generation via web API ---
    def generate_maze(self):
        url = f"https://pacmaz-s1-o.onrender.com/generate?width={self.MAZE_WIDTH}&height={self.MAZE_HEIGHT}&nbcycle={self.MAZE_NB_CYCLES}&nb_wrap_tunnels={self.MAZE_NUM_WRAP_TUNNELS}&nb_center_tunnels={self.MAZE_NUM_CENTER_TUNNELS}"
        response = urlopen(url)
        data_json = json.loads(response.read())
        self.maze = data_json.get("maze")
        self.height = data_json.get("height")
        self.width = data_json.get("width")


    def load_all_sprites(self):
        mapSpriteSheet = spritesheet.spritesheet('sprites/map_spriteSheet.png')
        self.mapImages = mapSpriteSheet.load_strip((0, 0, 16, 16), 16)
        for i in range(len(self.mapImages)):
            self.mapImages[i] = pygame.transform.scale(self.mapImages[i], (self.CELL_SIZE, self.CELL_SIZE))
        ghost_door = mapSpriteSheet.image_at((32, 16, 16, 16))
        self.ghost_door = pygame.transform.scale(ghost_door, (self.CELL_SIZE, self.CELL_SIZE))

        small_pellet = pygame.image.load("sprites/small_pellet.png")
        big_pellet = pygame.image.load("sprites/big_pellet.png")
        self.small_pellet = pygame.transform.scale(small_pellet, (self.CELL_SIZE, self.CELL_SIZE))
        self.big_pellet = pygame.transform.scale(big_pellet, (self.CELL_SIZE, self.CELL_SIZE))

        pacman = pygame.image.load("sprites/pacman_full.png")
        self.pacman_sprite = pygame.transform.scale(pacman, (self.CELL_SIZE, self.CELL_SIZE))
        pacman_right = pygame.image.load("sprites/pacman_right.png")
        self.pacman_right = pygame.transform.scale(pacman_right, (self.CELL_SIZE, self.CELL_SIZE))

        self.pacman_left = pygame.transform.flip(self.pacman_right, True, False)
        self.pacman_up = pygame.transform.rotate(self.pacman_right, 90)
        self.pacman_down = pygame.transform.flip(self.pacman_up, False, True)

        red_ghost_left = pygame.image.load("sprites/red_ghost_left1.png")
        self.red_ghost_left = pygame.transform.scale(red_ghost_left, (self.CELL_SIZE, self.CELL_SIZE))


    def generate_pelet(self):
        self.pellets = set()
        self.big_pellets = set()
        for y, row in enumerate(self.maze):
            for x, v in enumerate(row):
                try:
                    val = int(v)
                except Exception:
                    val = 1
                if val == 0:
                    if x != 0 and x != self.width - 1 and y != 0 and y != self.height - 1:
                        self.pellets.add((x, y))
        # remove pellet at starting position so pacman doesn't immediately eat one here
        # pellets.discard((pac_x, pac_y))
        # remove around ghost house 7 * 5
        for gy in range(self.height // 2 - 2, self.height // 2 + 3):
            for gx in range(self.width // 2 - 3, self.width // 2 + 4):
                self.pellets.discard((gx, gy))
        # place 4 big pellets near corners
        big_pellet_positions = [(1,1), (1,self.height-2), (self.width-2,1), (self.width-2,self.height-2)]
        for pos in big_pellet_positions:
            self.big_pellets.add(pos)
            # remove pellet at big pellet position so pacman doesn't immediately eat one here
            self.pellets.discard(pos)

    def wrap_coords(self, x, y):
        # wrap coordinates on torus
        return (x % self.width, y % self.height)

    def cell_free(self, x, y):
        wx, wy = self.wrap_coords(x, y)
        try:
            return int(self.maze[wy][wx]) == 0
        except Exception:
            return False

    def show_maze(self):
        floor_color = (0, 0, 0)
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        # directions2 = [(1,1),(-1,-1),(1,-1),(-1,1)]
        nbAdjacentWalls = 0
        left, right, up, down = 0, 0, 0, 0

        # create a background Surface with walls/floor drawn once (cheaper than redrawing grid each frame)
        self.bg = pygame.Surface((self.screen_w, self.screen_h))
        self.bg.fill(floor_color)
        for y, row in enumerate(self.maze):
            for x, v in enumerate(row):
                try:
                    val = int(v)
                except Exception:
                    val = 1
                if val == 1:
                    # check surrounding cells to choose correct wall tile
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if not self.cell_free(nx, ny):
                            nbAdjacentWalls += 1
                            if (dx, dy) == (-1, 0):
                                left = 1
                            if (dx, dy) == (1, 0):
                                right = 1
                            if (dx, dy) == (0, -1):
                                up = 1
                            if (dx, dy) == (0, 1):
                                down = 1
                    # choose tile based on wall neighbors
                    if nbAdjacentWalls == 0:
                        tile = 0  # isolated wall
                    elif nbAdjacentWalls == 1:
                        if left:
                            tile = 2
                        elif right:
                            tile = 4
                        elif up:
                            tile = 8
                        else:  # down
                            tile = 1
                    elif nbAdjacentWalls == 2:
                        if left and right:
                            tile = 6
                        elif up and down:
                            tile = 9
                        elif left and up:
                            tile = 10
                        elif left and down:
                            tile = 3
                        elif right and up:
                            tile = 12
                        else:  # right and down
                            tile = 5
                    elif nbAdjacentWalls == 3:
                        if not left:
                            tile = 13
                        elif not right:
                            tile = 11
                        elif not up:
                            tile = 7
                        else:  # not down
                            tile = 14
                    else:  # nbAdjacentWalls >= 4
                        # if nbAdjacentWalls >= 4:
                        #     for dx, dy in directions2:
                        #         nx, ny = x + dx, y + dy
                        #         if not cell_free(nx, ny):
                        #             tile = None
                        #             break
                        # else:
                        tile = 15
                    nbAdjacentWalls = 0
                    left, right, up, down = 0, 0, 0, 0
                    if tile is not None:
                        self.bg.blit(self.mapImages[tile], (x * self.CELL_SIZE, y * self.CELL_SIZE))
                    # draw wall tile

        
        # draw ghost house door on background as it's static
        self.door_x = self.width // 2
        self.door_y = self.height // 2 - 1
        self.bg.blit(self.ghost_door, (self.door_x * self.CELL_SIZE, self.door_y * self.CELL_SIZE))
        door_rect = pygame.Rect(self.door_x * self.CELL_SIZE, self.door_y * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
        pygame.draw.rect(self.bg, (252, 181, 255), door_rect)

    # helper to identify ghost-house door cell
    def is_ghost_house_door(self, x, y):
        wx, wy = self.wrap_coords(x, y)
        return (wx, wy) == (self.door_x, self.door_y)







    def process_events(self):
        running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.pacman.next_dir = (0, -1)
                elif event.key == pygame.K_DOWN:
                    self.pacman.next_dir = (0, 1)
                elif event.key == pygame.K_LEFT:
                    self.pacman.next_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.next_dir = (1, 0)
        return running



    def toroidal_delta(self, a, b, wrap):
        d = a - b
        if d > wrap / 2:
            d -= wrap
        elif d < -wrap / 2:
            d += wrap
        return d

    def run_logic(self):
        # if not win:
        if True:

            # ghost_x = width // 2
            # ghost_y = height // 2 - 2
            # ghost_pos = (ghost_x * CELL_SIZE, ghost_y * CELL_SIZE)
            
            # compute current integer cell center (in pixels)
            self.pacman.center_x = self.pacman.pac_x * self.CELL_SIZE + self.CELL_SIZE / 2
            self.pacman.center_y = self.pacman.pac_y * self.CELL_SIZE + self.CELL_SIZE / 2

            # are we exactly (or close enough) at the center of current cell? (use toroidal distance)
            at_center = abs(self.toroidal_delta(self.pacman.pac_px, self.pacman.center_x, self.screen_w)) < 1e-6 and abs(self.toroidal_delta(self.pacman.pac_py, self.pacman.center_y, self.screen_h)) < 1e-6

            # if at center, we can change direction: prefer next_dir
            if at_center:
                # snap to exact center to avoid float drift
                self.pacman.pac_px = self.pacman.center_x
                self.pacman.pac_py = self.pacman.center_y
                # try to take the player's desired turn first
                if self.pacman.next_dir != (0, 0):
                    tx, ty = self.pacman.pac_x + self.pacman.next_dir[0], self.pacman.pac_y + self.pacman.next_dir[1]
                    # block entering the ghost house through the door for Pacman
                    if self.cell_free(tx, ty) and not self.is_ghost_house_door(tx, ty):
                        self.pacman.current_dir = self.pacman.next_dir
                        self.pacman_sprite = {(0, -1): self.pacman_up,
                                (0, 1): self.pacman_down,
                                (-1, 0): self.pacman_left,
                                    (1, 0): self.pacman_right}[self.pacman.next_dir]
                    else:
                        # if desired direction blocked, keep going current_dir if possible
                        cx, cy = self.pacman.pac_x + self.pacman.current_dir[0], self.pacman.pac_y + self.pacman.current_dir[1]
                        # also prevent continuing into the ghost house door
                        if not self.cell_free(cx, cy) or self.is_ghost_house_door(cx, cy):
                            self.pacman.current_dir = (0, 0)
                else:
                    # no next direction requested: check if current_dir still possible
                    cx, cy = self.pacman.pac_x + self.pacman.current_dir[0], self.pacman.pac_y + self.pacman.current_dir[1]
                    # also prevent continuing into the ghost house door
                    if not self.cell_free(cx, cy) or self.is_ghost_house_door(cx, cy):
                        self.pacman.current_dir = (0, 0)

            # move along current_dir if allowed
            if self.pacman.current_dir != (0, 0):
                self.pacman.speed_px = self.pacman.MOVE_SPEED_CELLS_PER_SEC * self.CELL_SIZE
                # desired movement in pixels this frame
                self.pacman.move_x = self.pacman.current_dir[0] * self.pacman.speed_px * self.dt
                self.pacman.move_y = self.pacman.current_dir[1] * self.pacman.speed_px * self.dt

                # compute target cell (wrapped) and its center for the next cell in movement direction
                self.pacman.target_cell_x = (self.pacman.pac_x + self.pacman.current_dir[0]) % self.width
                self.pacman.target_cell_y = (self.pacman.pac_y + self.pacman.current_dir[1]) % self.height
                self.pacman.target_cx = self.pacman.target_cell_x * self.CELL_SIZE + self.CELL_SIZE / 2
                self.pacman.target_cy = self.pacman.target_cell_y * self.CELL_SIZE + self.CELL_SIZE / 2

                # distance remaining to the target center (use toroidal minimal distance)
                self.pacman.dist_x = self.toroidal_delta(self.pacman.target_cx, self.pacman.pac_px, self.screen_w)
                self.pacman.dist_y = self.toroidal_delta(self.pacman.target_cy, self.pacman.pac_py, self.screen_h)

                # if movement in this frame would overshoot the target center, snap to center and update grid cell
                if (abs(self.pacman.move_x) >= abs(self.pacman.dist_x) and self.pacman.current_dir[0] != 0) or (abs(self.pacman.move_y) >= abs(self.pacman.dist_y) and self.pacman.current_dir[1] != 0):
                    # snap to target center (and wrap grid coords)
                    self.pacman.pac_px = self.pacman.target_cx % self.screen_w
                    self.pacman.pac_py = self.pacman.target_cy % self.screen_h
                    self.pacman.pac_x = (self.pacman.pac_x + self.pacman.current_dir[0]) % self.width
                    self.pacman.pac_y = (self.pacman.pac_y + self.pacman.current_dir[1]) % self.height
                    # after arriving, allow immediate turn in the same frame on next loop iteration
                else:
                    self.pacman.pac_px += self.pacman.move_x
                    self.pacman.pac_py += self.pacman.move_y
                    # keep pixel position wrapped so drawing stays on-screen
                    self.pacman.pac_px %= self.screen_w
                    self.pacman.pac_py %= self.screen_h
            else:
                # not moving: keep pac centered on its grid cell (avoid drift)
                self.pacman.pac_px = self.pacman.pac_x * self.CELL_SIZE + self.CELL_SIZE / 2
                self.pacman.pac_py = self.pacman.pac_y * self.CELL_SIZE + self.CELL_SIZE / 2

            # If Pacman is on a pellet, eat it
            if (self.pacman.pac_x, self.pacman.pac_y) in self.pellets:
                self.pellets.remove((self.pacman.pac_x, self.pacman.pac_y))
                self.score += 10
            elif (self.pacman.pac_x, self.pacman.pac_y) in self.big_pellets:
                self.big_pellets.remove((self.pacman.pac_x, self.pacman.pac_y))
                self.score += 50

            # # if pacman on a ghost
            # if (self.pacman.pac_x, self.pacman.pac_y) == (ghost_x, ghost_y):
            #     lives -= 1
            #     # reset pacman position
            #     self.pacman.pac_x, self.pacman.pac_y = (self.width // 2 - 2, self.height - 2)
            #     self.pacman.pac_px = self.pacman.pac_x * self.CELL_SIZE + self.CELL_SIZE / 2
            #     self.pacman.pac_py = self.pacman.pac_y * self.CELL_SIZE + self.CELL_SIZE / 2
            #     current_dir = (0, 0)
            #     next_dir = (0, 0)
            #     if lives <= 0:
            #         running = False

            # if not self.pellets and not self.big_pellets:
            #     # all pellets eaten, end game
            #     win = True
            #     # running = False


    def display_frame(self):

        # draw background (walls + floor + door) from cached Surface
        self.screen.blit(self.bg, (0, 0))

        # draw pellets by iterating only active pellets (cheaper than scanning full grid)
        sp = self.small_pellet
        bp = self.big_pellet
        cs = self.CELL_SIZE
        for (x, y) in self.pellets:
            rect = pygame.Rect(x * cs, y * cs, cs, cs)
            self.screen.blit(sp, rect)
        for (x, y) in self.big_pellets:
            rect = pygame.Rect(x * cs, y * cs, cs, cs)
            self.screen.blit(bp, rect)

        # draw pacman
        center = (int(self.pacman.pac_px) - self.CELL_SIZE // 2, int(self.pacman.pac_py) - self.CELL_SIZE // 2)
        self.screen.blit(self.pacman_sprite, center)
        # self.screen.blit(self.red_ghost_left, self.ghost_pos)

        # # render score only when it changed
        # if self.score != self.last_score:
        #     try:
        #         score_surf = self.score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        #     except Exception:
        #         score_surf = None
        #     self.last_score = self.score
        # if score_surf:
        #     self.screen.blit(score_surf, (4, 4))

        # if self.lives > 0:
        #     for i in range(self.lives - 1):
        #         x = 4 + i * (self.CELL_SIZE + 4)
        #         y = self.screen_h - self.CELL_SIZE
        #         self.screen.blit(self.pacman_left, (x, y))

        # if self.win:
        #     win_surf = self.win_font.render(f"you win !", True, (255, 255, 255))
        #     self.screen.blit(win_surf, (self.screen_w // 2 - win_surf.get_width() // 2, self.screen_h // 2 - win_surf.get_height() // 2))
        pygame.display.flip()









# WIDTH = 19
# HEIGHT = 23

# NB_CYCLES = 10
# NUM_WRAP_TUNNELS = 2
# NUM_CENTER_TUNNELS = 5

# url = f"https://pacmaz-s1-o.onrender.com/generate?width={WIDTH}&height={HEIGHT}&nbcycle={NB_CYCLES}&nb_wrap_tunnels={NUM_WRAP_TUNNELS}&nb_center_tunnels={NUM_CENTER_TUNNELS}"
# response = urlopen(url)
# data_json = json.loads(response.read())

# # --- Simple pygame viewer + controllable Pacman (grid-based) ---
# def main():

#     def wrap_coords(x, y):
#         # wrap coordinates on torus
#         return (x % width, y % height)

#     def cell_free(x, y):
#         wx, wy = wrap_coords(x, y)
#         try:
#             return int(maze[wy][wx]) == 0
#         except Exception:
#             return False
        
    # # toroidal difference helper (returns shortest signed distance between a and b on a ring of size wrap)
    # def toroidal_delta(a, b, wrap):
    #     d = a - b
    #     if d > wrap / 2:
    #         d -= wrap
    #     elif d < -wrap / 2:
    #         d += wrap
    #     return d
    
    # extract maze from JSON -- expected format: data_json['maze'] is a list of rows with 0=empty, 1=wall
    # maze = data_json.get("maze")
    # if maze is None:
    #     raise RuntimeError("Couldn't find maze data in JSON (expected key 'maze')")

    # # maze: list of rows (height) each row is list of columns (width)
    # height = data_json.get("height")
    # width = data_json.get("width")

    # # screen_w = 466
    # # screen_h = 496

    # # CELL_SIZE = min(screen_w // width, screen_h // height)

    # MAX_PIX = 800
    # CELL_SIZE = max(8, min(32, MAX_PIX // max(1, width), MAX_PIX // max(1, height)))

    # screen_w = width * CELL_SIZE
    # screen_h = height * CELL_SIZE

    # pygame.init()
    # screen = pygame.display.set_mode((screen_w, screen_h))
    # pygame.display.set_caption("Pacman - arrow keys to move")
    # clock = pygame.time.Clock()
    # # target frames per second (lower => less CPU)
    # FPS = 60

    # movement speed (cells per second). Increase to make Pacman faster.
    # MOVE_SPEED_CELLS_PER_SEC = 7.0

    # # starting grid cell (integer indices) at bottom middle
    # pac_x, pac_y = (width // 2 - 2, height - 2)


    # # pixel position of Pacman's center (floats for smooth movement)
    # pac_px = pac_x * CELL_SIZE + CELL_SIZE / 2
    # pac_py = pac_y * CELL_SIZE + CELL_SIZE / 2

    # # movement directions: current movement and next desired direction
    # current_dir = (0, 0)
    # next_dir = (0, 0)

    # mapSpriteSheet = spritesheet.spritesheet('sprites/map_spriteSheet.png')
    # mapImages = mapSpriteSheet.load_strip((0, 0, 16, 16), 16)
    # for i in range(len(mapImages)):
    #     mapImages[i] = pygame.transform.scale(mapImages[i], (CELL_SIZE, CELL_SIZE))
    # ghost_door = mapSpriteSheet.image_at((32, 16, 16, 16))
    # ghost_door = pygame.transform.scale(ghost_door, (CELL_SIZE, CELL_SIZE))

    # small_pellet = pygame.image.load("sprites/small_pellet.png")
    # big_pellet = pygame.image.load("sprites/big_pellet.png")
    # small_pellet = pygame.transform.scale(small_pellet, (CELL_SIZE, CELL_SIZE))
    # big_pellet = pygame.transform.scale(big_pellet, (CELL_SIZE, CELL_SIZE))

    # pacman = pygame.image.load("sprites/pacman_full.png")
    # pacman = pygame.transform.scale(pacman, (CELL_SIZE, CELL_SIZE))
    # pacman_right = pygame.image.load("sprites/pacman_right.png")
    # pacman_right = pygame.transform.scale(pacman_right, (CELL_SIZE, CELL_SIZE))

    # pacman_left = pygame.transform.flip(pacman_right, True, False)
    # pacman_up = pygame.transform.rotate(pacman_right, 90)
    # pacman_down = pygame.transform.flip(pacman_up, False, True)

    # red_ghost_left = pygame.image.load("sprites/red_ghost_left1.png")
    # red_ghost_left = pygame.transform.scale(red_ghost_left, (CELL_SIZE, CELL_SIZE))

    # # score and pellets initialization: place a pellet on every empty cell (maze cell == 0)
    # score = 0
    # lives = 3

    # pellets = set()
    # big_pellets = set()
    # for y, row in enumerate(maze):
    #     for x, v in enumerate(row):
    #         try:
    #             val = int(v)
    #         except Exception:
    #             val = 1
    #         if val == 0:
    #             if x != 0 and x != width - 1 and y != 0 and y != height - 1:
    #                 pellets.add((x, y))
    # # remove pellet at starting position so pacman doesn't immediately eat one here
    # pellets.discard((pac_x, pac_y))
    # # remove around ghost house 7 * 5
    # for gy in range(height // 2 - 2, height // 2 + 3):
    #     for gx in range(width // 2 - 3, width // 2 + 4):
    #         pellets.discard((gx, gy))
    # # place 4 big pellets near corners
    # big_pellet_positions = [(1,1), (1,height-2), (width-2,1), (width-2,height-2)]
    # for pos in big_pellet_positions:
    #     big_pellets.add(pos)
    #     # remove pellet at big pellet position so pacman doesn't immediately eat one here
    #     pellets.discard(pos)
    

    # prepare font for score display

    ####################################################
    # pygame.font.init()
    # score_font = pygame.font.SysFont(None, max(18, CELL_SIZE // 2))
    # win_font = pygame.font.SysFont(None, 90)
    ####################################################

    # # colors used for background drawing
    # # wall_color = (34, 49, 184)
    # floor_color = (0, 0, 0)

    # directions = [(1,0),(-1,0),(0,1),(0,-1)]
    # # directions2 = [(1,1),(-1,-1),(1,-1),(-1,1)]
    # nbAdjacentWalls = 0
    # left, right, up, down = 0, 0, 0, 0

    # create a background Surface with walls/floor drawn once (cheaper than redrawing grid each frame)
    # bg = pygame.Surface((screen_w, screen_h))
    # bg.fill(floor_color)
    # for y, row in enumerate(maze):
    #     for x, v in enumerate(row):
    #         try:
    #             val = int(v)
    #         except Exception:
    #             val = 1
    #         if val == 1:
    #             # check surrounding cells to choose correct wall tile
    #             for dx, dy in directions:
    #                 nx, ny = x + dx, y + dy
    #                 if not cell_free(nx, ny):
    #                     nbAdjacentWalls += 1
    #                     if (dx, dy) == (-1, 0):
    #                         left = 1
    #                     if (dx, dy) == (1, 0):
    #                         right = 1
    #                     if (dx, dy) == (0, -1):
    #                         up = 1
    #                     if (dx, dy) == (0, 1):
    #                         down = 1
    #             # choose tile based on wall neighbors
    #             if nbAdjacentWalls == 0:
    #                 tile = 0  # isolated wall
    #             elif nbAdjacentWalls == 1:
    #                 if left:
    #                     tile = 2
    #                 elif right:
    #                     tile = 4
    #                 elif up:
    #                     tile = 8
    #                 else:  # down
    #                     tile = 1
    #             elif nbAdjacentWalls == 2:
    #                 if left and right:
    #                     tile = 6
    #                 elif up and down:
    #                     tile = 9
    #                 elif left and up:
    #                     tile = 10
    #                 elif left and down:
    #                     tile = 3
    #                 elif right and up:
    #                     tile = 12
    #                 else:  # right and down
    #                     tile = 5
    #             elif nbAdjacentWalls == 3:
    #                 if not left:
    #                     tile = 13
    #                 elif not right:
    #                     tile = 11
    #                 elif not up:
    #                     tile = 7
    #                 else:  # not down
    #                     tile = 14
    #             else:  # nbAdjacentWalls >= 4
    #                 # if nbAdjacentWalls >= 4:
    #                 #     for dx, dy in directions2:
    #                 #         nx, ny = x + dx, y + dy
    #                 #         if not cell_free(nx, ny):
    #                 #             tile = None
    #                 #             break
    #                 # else:
    #                 tile = 15
    #             nbAdjacentWalls = 0
    #             left, right, up, down = 0, 0, 0, 0
    #             if tile is not None:
    #                 bg.blit(mapImages[tile], (x * CELL_SIZE, y * CELL_SIZE))
    #             # draw wall tile

    
    # # draw ghost house door on background as it's static
    # door_x = width // 2
    # door_y = height // 2 - 1
    # bg.blit(ghost_door, (door_x * CELL_SIZE, door_y * CELL_SIZE))
    # # door_rect = pygame.Rect(door_x * CELL_SIZE, door_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    # # pygame.draw.rect(bg, (252, 181, 255), door_rect)

    # # helper to identify ghost-house door cell
    # def is_ghost_house_door(x, y):
    #     wx, wy = wrap_coords(x, y)
    #     return (wx, wy) == (door_x, door_y)

    # score surface cache to avoid rerendering each frame
    ####################################################

    # last_score = None
    # score_surf = None

    # win = False
    ####################################################

    # running = True
    # while running:
    #     # dt in seconds since last frame (use FPS cap)
    #     dt = clock.tick(FPS) / 1000.0

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False
        #     elif event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_UP:
        #             next_dir = (0, -1)
        #         elif event.key == pygame.K_DOWN:
        #             next_dir = (0, 1)
        #         elif event.key == pygame.K_LEFT:
        #             next_dir = (-1, 0)
        #         elif event.key == pygame.K_RIGHT:
        #             next_dir = (1, 0)

        # if not win:

        #     ghost_x = width // 2
        #     ghost_y = height // 2 - 2
        #     ghost_pos = (ghost_x * CELL_SIZE, ghost_y * CELL_SIZE)
            
        #     # compute current integer cell center (in pixels)
        #     center_x = pac_x * CELL_SIZE + CELL_SIZE / 2
        #     center_y = pac_y * CELL_SIZE + CELL_SIZE / 2

        #     # are we exactly (or close enough) at the center of current cell? (use toroidal distance)
        #     at_center = abs(toroidal_delta(pac_px, center_x, screen_w)) < 1e-6 and abs(toroidal_delta(pac_py, center_y, screen_h)) < 1e-6

        #     # if at center, we can change direction: prefer next_dir
        #     if at_center:
        #         # snap to exact center to avoid float drift
        #         pac_px = center_x
        #         pac_py = center_y
        #         # try to take the player's desired turn first
        #         if next_dir != (0, 0):
        #             tx, ty = pac_x + next_dir[0], pac_y + next_dir[1]
        #             # block entering the ghost house through the door for Pacman
        #             if cell_free(tx, ty) and not is_ghost_house_door(tx, ty):
        #                 current_dir = next_dir
        #                 pacman = {(0, -1): pacman_up,
        #                         (0, 1): pacman_down,
        #                         (-1, 0): pacman_left,
        #                             (1, 0): pacman_right}[next_dir]
        #             else:
        #                 # if desired direction blocked, keep going current_dir if possible
        #                 cx, cy = pac_x + current_dir[0], pac_y + current_dir[1]
        #                 # also prevent continuing into the ghost house door
        #                 if not cell_free(cx, cy) or is_ghost_house_door(cx, cy):
        #                     current_dir = (0, 0)
        #         else:
        #             # no next direction requested: check if current_dir still possible
        #             cx, cy = pac_x + current_dir[0], pac_y + current_dir[1]
        #             # also prevent continuing into the ghost house door
        #             if not cell_free(cx, cy) or is_ghost_house_door(cx, cy):
        #                 current_dir = (0, 0)

        #     # move along current_dir if allowed
        #     if current_dir != (0, 0):
        #         speed_px = MOVE_SPEED_CELLS_PER_SEC * CELL_SIZE
        #         # desired movement in pixels this frame
        #         move_x = current_dir[0] * speed_px * dt
        #         move_y = current_dir[1] * speed_px * dt

        #         # compute target cell (wrapped) and its center for the next cell in movement direction
        #         target_cell_x = (pac_x + current_dir[0]) % width
        #         target_cell_y = (pac_y + current_dir[1]) % height
        #         target_cx = target_cell_x * CELL_SIZE + CELL_SIZE / 2
        #         target_cy = target_cell_y * CELL_SIZE + CELL_SIZE / 2

        #         # distance remaining to the target center (use toroidal minimal distance)
        #         dist_x = toroidal_delta(target_cx, pac_px, screen_w)
        #         dist_y = toroidal_delta(target_cy, pac_py, screen_h)

        #         # if movement in this frame would overshoot the target center, snap to center and update grid cell
        #         if (abs(move_x) >= abs(dist_x) and current_dir[0] != 0) or (abs(move_y) >= abs(dist_y) and current_dir[1] != 0):
        #             # snap to target center (and wrap grid coords)
        #             pac_px = target_cx % screen_w
        #             pac_py = target_cy % screen_h
        #             pac_x = (pac_x + current_dir[0]) % width
        #             pac_y = (pac_y + current_dir[1]) % height
        #             # after arriving, allow immediate turn in the same frame on next loop iteration
        #         else:
        #             pac_px += move_x
        #             pac_py += move_y
        #             # keep pixel position wrapped so drawing stays on-screen
        #             pac_px %= screen_w
        #             pac_py %= screen_h
        #     else:
        #         # not moving: keep pac centered on its grid cell (avoid drift)
        #         pac_px = pac_x * CELL_SIZE + CELL_SIZE / 2
        #         pac_py = pac_y * CELL_SIZE + CELL_SIZE / 2

        #     # If Pacman is on a pellet, eat it
        #     if (pac_x, pac_y) in pellets:
        #         pellets.remove((pac_x, pac_y))
        #         score += 10
        #     elif (pac_x, pac_y) in big_pellets:
        #         big_pellets.remove((pac_x, pac_y))
        #         score += 50

        #     # if pacman on a ghost
        #     if (pac_x, pac_y) == (ghost_x, ghost_y):
        #         lives -= 1
        #         # reset pacman position
        #         pac_x, pac_y = (width // 2 - 2, height - 2)
        #         pac_px = pac_x * CELL_SIZE + CELL_SIZE / 2
        #         pac_py = pac_y * CELL_SIZE + CELL_SIZE / 2
        #         current_dir = (0, 0)
        #         next_dir = (0, 0)
        #         if lives <= 0:
        #             running = False

        #     if not pellets and not big_pellets:
        #         # all pellets eaten, end game
        #         win = True
        #         # running = False





        # --- Drawing code ---

        # draw background (walls + floor + door) from cached Surface
    #     screen.blit(bg, (0, 0))

    #     # draw pellets by iterating only active pellets (cheaper than scanning full grid)
    #     sp = small_pellet
    #     bp = big_pellet
    #     cs = CELL_SIZE
    #     for (x, y) in pellets:
    #         rect = pygame.Rect(x * cs, y * cs, cs, cs)
    #         screen.blit(sp, rect)
    #     for (x, y) in big_pellets:
    #         rect = pygame.Rect(x * cs, y * cs, cs, cs)
    #         screen.blit(bp, rect)

    #     # draw pacman
    #     center = (int(pac_px) - CELL_SIZE // 2, int(pac_py) - CELL_SIZE // 2)
    #     screen.blit(pacman, center)

    #     screen.blit(red_ghost_left, ghost_pos)

    #     # render score only when it changed
    #     if score != last_score:
    #         try:
    #             score_surf = score_font.render(f"Score: {score}", True, (255, 255, 255))
    #         except Exception:
    #             score_surf = None
    #         last_score = score
    #     if score_surf:
    #         screen.blit(score_surf, (4, 4))

    #     if lives > 0:
    #         for i in range(lives - 1):
    #             x = 4 + i * (CELL_SIZE + 4)
    #             y = screen_h - CELL_SIZE
    #             screen.blit(pacman_left, (x, y))

    #     if win:
    #         win_surf = win_font.render(f"you win !", True, (255, 255, 255))
    #         screen.blit(win_surf, (screen_w // 2 - win_surf.get_width() // 2, screen_h // 2 - win_surf.get_height() // 2))

    #     pygame.display.flip()

    # pygame.quit()


# if __name__ == "__main__":
#     main()