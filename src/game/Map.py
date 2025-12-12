import pygame
import Spritesheet

class Map:
    def __init__(self, maze, width, height, max_pix, maze_id = None):

        self.maze = maze
        self.width = width
        self.height = height
        self.maze_id = maze_id

        self.mapImages = []
        self.ghost_door = None
        self.MAX_PIX = max_pix
        self.CELL_SIZE = max(8, min(32, self.MAX_PIX // max(1, self.width), self.MAX_PIX // max(1, self.height + 3)))
        self.game_screen = pygame.Surface((self.width * self.CELL_SIZE, self.height * self.CELL_SIZE))
        self.game_screen_w = self.game_screen.get_width()
        self.game_screen_h = self.game_screen.get_height()
        self.bg = None
        self.load_map_sprites()
        self.add_walls()


    def load_map_sprites(self):
        mapSpriteSheet = Spritesheet.Spritesheet('sprites/map_spriteSheet.bmp')
        self.mapImages = mapSpriteSheet.load_strip((0, 0, 16, 16), 16, -1)
        for i in range(len(self.mapImages)):
            self.mapImages[i] = self.resize_sprites(self.mapImages[i])

        ghost_door = mapSpriteSheet.image_at((32, 16, 16, 16), -1)
        self.ghost_door = self.resize_sprites(ghost_door)

    def resize_sprites(self, image):
        image = pygame.transform.scale(image, (self.CELL_SIZE, self.CELL_SIZE)).convert_alpha()
        return image


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
        # self.update_pellets_screen()

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

    def cell_free(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return int(self.maze[y][x]) == 0