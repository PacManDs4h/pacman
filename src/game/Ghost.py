import pygame
from SpriteStripAnim import SpriteStripAnim
import move
import random

class Ghost():
    """ This class represents a ghost. """
    def __init__(self, game, color, start_x, start_y):
        self.game = game
        self.color = color

        self.start_x = start_x
        self.start_y = start_y

        self.MOVE_SPEED_CELLS_PER_SEC = 4.5
        
        self.x = start_x
        self.y = start_y

        self.px = self.x * game.CELL_SIZE + game.CELL_SIZE / 2
        self.py = self.y * game.CELL_SIZE + game.CELL_SIZE / 2

        self.current_dir = (0, 0)
        self.next_dir = (0, 0)

        self.center_x = 0
        self.center_y = 0

        self.speed_px = 0

        self.strips = []
        self.n = 0

        self.top_left = (0, 0)
        self.center = (0, 0)

        self.chase = True

        self.load_sprites()
    

    def load_sprites(self):
        frames = 12
        color = str(self.color)
        
        self.strips = [
            SpriteStripAnim(f'sprites/{color}_ghost_sprite_sheet.bmp', (0,0,14,14), 2, -1, True, frames),
            SpriteStripAnim(f'sprites/{color}_ghost_sprite_sheet.bmp', (0,14,14,14), 2, -1, True, frames),
            SpriteStripAnim(f'sprites/{color}_ghost_sprite_sheet.bmp', (0,28,14,14), 2, -1, True, frames),
            SpriteStripAnim(f'sprites/{color}_ghost_sprite_sheet.bmp', (0,42,14,14), 2, -1, True, frames),
        ]

        for j in range(len(self.strips)):
            for i in range(len(self.strips[j].images)):
                self.strips[j].images[i] = pygame.transform.scale(self.strips[j].images[i], (self.game.CELL_SIZE, self.game.CELL_SIZE))
        self.current_sprite = self.strips[self.n].next()
    
    def reset_position(self):
        """ Reset Ghost's position to the starting location. """
        self.x = self.start_x
        self.y = self.start_y
        self.px = self.x * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
        self.py = self.y * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
        self.current_dir = (0, 0)
        self.next_dir = (0, 0)

    def mouv_ghost(self):
        start_pos = (int(self.x), int(self.y))
        
        pacman_pos = (int(self.game.pacman.x), int(self.game.pacman.y))
        
        path = self.game.get_path_bfs(start_pos, pacman_pos)
        
        if path:
            # La prochaine case où aller est la première du chemin
            next_cell = path[0] 
            nx, ny = next_cell
            
            dx = nx - start_pos[0]
            dy = ny - start_pos[1]
            self.next_dir = (dx, dy)
        else:
            # Si pas de chemin trouvé, mouvement aléatoire
            self.next_dir = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
            if self.next_dir == (-self.current_dir[0], -self.current_dir[1]):
                self.next_dir = self.current_dir

        if self.chase == True:
            self.MOVE_SPEED_CELLS_PER_SEC = 4.
        else:
            self.MOVE_SPEED_CELLS_PER_SEC = 2.5

        in_house = False

        if self.color == "red":
            pass
            # go towards pacman
        
        elif self.color == "blue":
            if self.game.score >= 300:
                in_house = False
            else:
                in_house = True
            
        elif self.color == "orange":
            if self.game.score >= 600:
                in_house = False
            else:
                in_house = True

        move.get_direction(self, in_house)
        move.move(self)

    def update(self):
        """ Update the ghost location. """
        self.mouv_ghost()





