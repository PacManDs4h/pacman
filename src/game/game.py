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
        self.MAZE_NUM_CENTER_TUNNELS = 7

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
        self.lives_sprite = None

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

        self.game_screen = pygame.Surface((self.MAZE_WIDTH * self.CELL_SIZE, self.MAZE_HEIGHT * self.CELL_SIZE))
        self.game_screen_w = self.game_screen.get_width()
        self.game_screen_h = self.game_screen.get_height()

        self.score_font = pygame.font.Font("fonts/emulogic.ttf", max(18, self.CELL_SIZE // 2))
        self.win_font = pygame.font.Font("fonts/emulogic.ttf", 90)

        self.load_map_sprites()
        self.pacman = Pacman.Pacman(self)
        self.red_ghost = Ghost.Ghost(self, "red", self.width // 2, self.height // 2 - 2)
        self.blue_ghost = Ghost.Ghost(self, "blue", self.width // 2 - 1 , self.height // 2)
        self.pink_ghost = Ghost.Ghost(self, "pink", self.width // 2, self.height // 2)
        self.orange_ghost = Ghost.Ghost(self, "orange", self.width // 2 + 1, self.height // 2)
        self.generate_pelet()
        self.add_walls()

        self.offset_x = (self.screen_w // 2) - (self.game_screen_w // 2)
        self.offset_y = (self.screen_h // 2) - (self.game_screen_h // 2)

        self.ghosts_pos = []



    # --- Maze generation via web API ---
    def generate_maze(self):
        url = f"https://pacmaz-s1-o.onrender.com/generate?width={self.MAZE_WIDTH}&height={self.MAZE_HEIGHT}&nbcycle={self.MAZE_NB_CYCLES}&nb_wrap_tunnels={self.MAZE_NUM_WRAP_TUNNELS}&nb_center_tunnels={self.MAZE_NUM_CENTER_TUNNELS}"
        response = urlopen(url)
        data_json = json.loads(response.read())
        self.maze = data_json.get("maze")
        self.height = data_json.get("height")
        self.width = data_json.get("width")


    def load_map_sprites(self):
        mapSpriteSheet = spritesheet.spritesheet('sprites/map_spriteSheet.bmp')
        self.mapImages = mapSpriteSheet.load_strip((0, 0, 16, 16), 16, -1)
        for i in range(len(self.mapImages)):
            self.mapImages[i] = self.resize_sprites(self.mapImages[i])

        ghost_door = mapSpriteSheet.image_at((32, 16, 16, 16), -1)
        self.ghost_door = self.resize_sprites(ghost_door)

        small_pellet = pygame.image.load("sprites/small_pellet.png")
        big_pellet = pygame.image.load("sprites/big_pellet.png")
        self.small_pellet = self.resize_sprites(small_pellet)
        self.big_pellet = self.resize_sprites(big_pellet)

        self.lives_sprite = self.resize_sprites(pygame.image.load("sprites/pacman_left.png"))


    def resize_sprites(self, image):
        image = pygame.transform.scale(image, (self.CELL_SIZE, self.CELL_SIZE)).convert_alpha()
        return image


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
        self.pellets.discard((self.pacman.x, self.pacman.y))
        # remove around ghost house 7 * 5
        for gy in range(self.height // 2 - 3, self.height // 2 + 3):
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
        self.bg = pygame.Surface((self.game_screen_w, self.game_screen_h))
        self.bg.fill(floor_color)

        for y, row in enumerate(self.maze):
            for x, v in enumerate(row):
                try:
                    val = int(v)
                except Exception:
                    val = 1
                if val == 1:
                    tile = 0
                    if not self.cell_free(x, y-1): tile |= 1   # haut
                    if not self.cell_free(x+1, y): tile |= 2   # droite
                    if not self.cell_free(x, y+1): tile |= 4   # bas
                    if not self.cell_free(x-1, y): tile |= 8   # gauche

                    if x == 0 and ((y-1 >= 0 and self.cell_free(x, y-1)) or (y+1 < self.height and self.cell_free(x, y+1))):
                        tile |= 8
                    if x == self.width-1 and ((y-1 >= 0 and self.cell_free(x, y-1)) or (y+1 < self.height and self.cell_free(x, y+1))):
                        tile |= 2

                    self.bg.blit(self.mapImages[tile], (x * self.CELL_SIZE, y * self.CELL_SIZE))

        # draw ghost house door on background as it's static
        self.door_x = self.width // 2
        self.door_y = self.height // 2 - 1
        self.bg.blit(self.ghost_door, (self.door_x * self.CELL_SIZE, self.door_y * self.CELL_SIZE))

        if (self.width // 2) % 2 == 1:  # seulement si il y a la colonne de 3 de large
            self.vertical_streak()
        self.update_pellets_screen()
    

    # fonctions utilisées pour combler les cercles dans les murs de la colonne centrale
    def vertical_streak(self):
        start = None
        count = 0
        for i in range(self.height):
            if not self.cell_free(self.door_x, i):
                # début d’un nouveau streak
                if count == 0:
                    start = i
                count += 1
            else:
                # fin d’un streak
                if count >= 2:
                    self.draw_block(start, count)
                count = 0
        # gérer un streak qui se termine à la dernière ligne
        if count >= 2:
            self.draw_block(start, count)

    def draw_block(self, start, count):
        start_x = ((self.door_x - 1) * self.CELL_SIZE) + self.CELL_SIZE // 2
        start_y = (start) * (self.CELL_SIZE) + self.CELL_SIZE // 2
        rect = pygame.Rect(start_x, start_y, self.CELL_SIZE * 2, (self.CELL_SIZE * count) - self.CELL_SIZE )
        pygame.draw.rect(self.bg, (0,0,0), rect, width=0)



    # helper to identify ghost-house door cell
    def is_ghost_house_door(self, x, y):
        return (x, y) == (self.door_x, self.door_y)

    def cell_free(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return int(self.maze[y][x]) == 0

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
            self.blue_ghost.update()
            self.pink_ghost.update()
            self.orange_ghost.update()
            self.ghosts_pos = [(self.red_ghost.x, self.red_ghost.y), (self.blue_ghost.x, self.blue_ghost.y), (self.pink_ghost.x, self.pink_ghost.y), (self.orange_ghost.x, self.orange_ghost.y)]

    def reset(self):
        self.pacman.reset_position()
        self.red_ghost.reset_position()
        self.blue_ghost.reset_position()
        self.pink_ghost.reset_position()
        self.orange_ghost.reset_position()

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
        self.game_screen.blit(self.pacman.current_sprite, self.pacman.center)

        self.game_screen.blit(self.red_ghost.current_sprite, (self.red_ghost.center))
        self.game_screen.blit(self.blue_ghost.current_sprite, (self.blue_ghost.center))
        self.game_screen.blit(self.pink_ghost.current_sprite, (self.pink_ghost.center))
        self.game_screen.blit(self.orange_ghost.current_sprite, (self.orange_ghost.center))

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
                self.screen.blit(self.lives_sprite, (x, y))

        if self.win:
            win_surf = self.win_font.render(f"you win !", True, (255, 255, 255))
            self.screen.blit(win_surf, (self.screen_w // 2 - win_surf.get_width() // 2, self.screen_h // 2 - win_surf.get_height() // 2))
        
        pygame.display.flip()
        