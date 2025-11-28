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

        self.MOVE_SPEED_CELLS_PER_SEC = 6.5
        
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

        self.center = (0, 0)

        self.hitbox = pygame.Rect(self.px, self.py, 0, 0)

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

    def update(self):
        """ Update the ghost location. """
        # can't be oposite of current direction
        self.next_dir = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        if self.next_dir == (-self.current_dir[0], -self.current_dir[1]):
            self.next_dir = self.current_dir

        move.get_direction(self, False)
        move.move(self)
        self.hitbox = pygame.Rect(self.px, self.py, 0, 0)
        self.hitbox = self.hitbox.inflate(self.game.CELL_SIZE // 2 , self.game.CELL_SIZE // 2)
