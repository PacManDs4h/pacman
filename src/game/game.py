import json
from urllib.request import urlopen
import pygame
import spritesheet
import Pacman
import Ghost

class Game:
    def __init__(self, screen):
        self.MAZE_WIDTH = 19
        self.MAZE_HEIGHT = 21 
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

        self.door_x = 0
        self.door_y = 0

        self.maze = []
        self.height = 0
        self.width = 0

        self.dt = 0
        
        self.last_score = None
        self.score_surf = None
        self.win = False
        self.running = True

        self.bg = None
        self.pellets_screen = pygame.Surface((self.screen_w, self.screen_h))


        self.generate_maze()

        self.CELL_SIZE = max(8, min(32, self.MAX_PIX // max(1, self.width), self.MAX_PIX // max(1, self.height + 3)))
        print(f"Cell size: {self.CELL_SIZE}")

        self.game_screen = pygame.Surface((self.MAZE_WIDTH * self.CELL_SIZE, self.MAZE_HEIGHT * self.CELL_SIZE))
        self.game_screen_w = self.game_screen.get_width()
        self.game_screen_h = self.game_screen.get_height()

        self.score_font = pygame.font.Font("fonts/emulogic.ttf", max(18, self.CELL_SIZE // 2))
        self.win_font = pygame.font.Font("fonts/emulogic.ttf", 90)

        self.load_map_sprites()
        self.pacman = Pacman.Pacman(self)
        self.red_ghost = Ghost.Ghost(self, "red", self.width // 2, self.height // 2 - 2)
        self.generate_pelet()
        self.add_walls()

        self.offset_x = (self.screen_w // 2) - (self.game_screen_w // 2)
        self.offset_y = (self.screen_h // 2) - (self.game_screen_h // 2)



    # --- Maze generation via web API ---
    def generate_maze(self):
        url = f"https://pacmaz-s1-o.onrender.com/generate?width={self.MAZE_WIDTH}&height={self.MAZE_HEIGHT}&nbcycle={self.MAZE_NB_CYCLES}&nb_wrap_tunnels={self.MAZE_NUM_WRAP_TUNNELS}&nb_center_tunnels={self.MAZE_NUM_CENTER_TUNNELS}"
        response = urlopen(url)
        data_json = json.loads(response.read())
        self.maze = data_json.get("maze")
        self.height = data_json.get("height")
        self.width = data_json.get("width")


    def load_map_sprites(self):
        mapSpriteSheet = spritesheet.spritesheet('sprites/map_spriteSheet.png')
        self.mapImages = mapSpriteSheet.load_strip((0, 0, 16, 16), 16)
        for i in range(len(self.mapImages)):
            self.mapImages[i] = pygame.transform.scale(self.mapImages[i], (self.CELL_SIZE, self.CELL_SIZE)).convert()
        ghost_door = mapSpriteSheet.image_at((32, 16, 16, 16))
        self.ghost_door = pygame.transform.scale(ghost_door, (self.CELL_SIZE, self.CELL_SIZE)).convert()

        small_pellet = pygame.image.load("sprites/small_pellet.png")
        big_pellet = pygame.image.load("sprites/big_pellet.png")
        self.small_pellet = pygame.transform.scale(small_pellet, (self.CELL_SIZE, self.CELL_SIZE)).convert()
        self.big_pellet = pygame.transform.scale(big_pellet, (self.CELL_SIZE, self.CELL_SIZE)).convert()


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
        self.pellets.discard((self.pacman.pac_x, self.pacman.pac_y))
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


    def add_walls(self):
        floor_color = (0, 0, 0)
        directions = [(1,0),(-1,0),(0,1),(0,-1)]
        # directions2 = [(1,1),(-1,-1),(1,-1),(-1,1)]
        nbAdjacentWalls = 0
        left, right, up, down = 0, 0, 0, 0

        # create a background Surface with walls/floor drawn once (cheaper than redrawing grid each frame)
        # self.bg = pygame.Surface((self.screen_w, self.screen_h))
        self.bg = pygame.Surface((self.game_screen_w, self.game_screen_h))
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

        self.update_pellets_screen()


    # helper to identify ghost-house door cell
    def is_ghost_house_door(self, x, y):
        wx, wy = self.wrap_coords(x, y)
        return (wx, wy) == (self.door_x, self.door_y)

    def wrap_coords(self, x, y):
        # wrap coordinates on torus
        return (x % self.width, y % self.height)

    def cell_free(self, x, y):
        wx, wy = self.wrap_coords(x, y)
        try:
            return int(self.maze[wy][wx]) == 0
        except Exception:
            return False


    def toroidal_delta(self, a, b, wrap):
        d = a - b
        if d > wrap / 2:
            d -= wrap
        elif d < -wrap / 2:
            d += wrap
        return d


    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.pacman.next_dir = (0, -1)
                elif event.key == pygame.K_DOWN:
                    self.pacman.next_dir = (0, 1)
                elif event.key == pygame.K_LEFT:
                    self.pacman.next_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.next_dir = (1, 0)
        return self.running


    def run_logic(self):
        if not self.win:
            self.pacman.update()
            self.red_ghost.update()


    def update_pellets_screen(self):
        self.pellets_screen.blit(self.bg, (0, 0))
        sp = self.small_pellet
        bp = self.big_pellet
        cs = self.CELL_SIZE
        for (x, y) in self.pellets:
            rect = pygame.Rect(x * cs, y * cs, cs, cs)
            self.pellets_screen.blit(sp, rect)
        for (x, y) in self.big_pellets:
            rect = pygame.Rect(x * cs, y * cs, cs, cs)
            self.pellets_screen.blit(bp, rect)


    def display_frame(self):

        self.screen.fill((0, 0, 0))
        # draw background (walls + floor + door) from cached Surface
        self.game_screen.blit(self.pellets_screen, (0, 0))

        # draw pacman
        center = (int(self.pacman.pac_px) - self.CELL_SIZE // 2, int(self.pacman.pac_py) - self.CELL_SIZE // 2)
        self.game_screen.blit(self.pacman.pacman_sprite, center)

        self.game_screen.blit(self.red_ghost.ghost_sprite, (int(self.red_ghost.ghost_x * self.CELL_SIZE), int(self.red_ghost.ghost_y * self.CELL_SIZE)))

        self.screen.blit(self.game_screen, (self.offset_x, self.offset_y))

        # render score only when it changed
        if self.score != self.last_score:
            try:
                self.score_surf = self.score_font.render(f"Score {self.score}", False, (255, 255, 255))
            except Exception:
                self.score_surf = None
            self.last_score = self.score
        if self.score_surf:
            self.screen.blit(self.score_surf, (self.offset_x, self.offset_y - 30))

        if self.lives > 0:
            for i in range(self.lives - 1):
                x = self.offset_x + 4 + i * (self.CELL_SIZE + 4)
                y = self.game_screen_h + self.offset_y + 4
                self.screen.blit(self.pacman.pacman_left, (x, y))

        if self.win:
            win_surf = self.win_font.render(f"you win !", True, (255, 255, 255))
            self.screen.blit(win_surf, (self.screen_w // 2 - win_surf.get_width() // 2, self.screen_h // 2 - win_surf.get_height() // 2))
        
        pygame.display.flip()
        