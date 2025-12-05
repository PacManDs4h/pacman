import pygame
from SpriteStripAnim import SpriteStripAnim
import move

class Pacman():
    """ This class represents the player. """
    def __init__(self, game):
        self.game = game
        
        self.MOVE_SPEED_CELLS_PER_SEC = 5.0
        self.x, self.y = (game.width // 2 - 2, game.height - 2)

        # pixel position of Pacman's center (floats for smooth movement)
        self.px = self.x * game.CELL_SIZE + game.CELL_SIZE / 2
        self.py = self.y * game.CELL_SIZE + game.CELL_SIZE / 2

        # movement directions: current movement and next desired direction
        self.current_dir = (0, 0)
        self.next_dir = (0, 0)

        self.center_x = 0
        self.center_y = 0

        self.speed_px = 0

        self.strips = []
        self.n = 0

        self.top_left = (0, 0)
        self.center = (0, 0)

        self.hitbox = pygame.Rect(self.center[0], self.center[1], 0, 0)

        self.save = ""


        self.load_sprites()

 
    def load_sprites(self):
        frames = 3
        self.strips = [
            SpriteStripAnim('sprites/pacman_sprite_sheet.bmp', (0,0,13,13), 4, -1, True, frames),
            SpriteStripAnim('sprites/pacman_sprite_sheet.bmp', (0,13,13,13), 4, -1, True, frames),
            SpriteStripAnim('sprites/pacman_sprite_sheet.bmp', (0,26,13,13), 4, -1, True, frames),
            SpriteStripAnim('sprites/pacman_sprite_sheet.bmp', (0,39,13,13), 4, -1, True, frames),
        ]
        for j in range(len(self.strips)):
            for i in range(len(self.strips[j].images)):
                self.strips[j].images[i] = pygame.transform.scale(self.strips[j].images[i], (self.game.CELL_SIZE, self.game.CELL_SIZE))

        pacman = pygame.image.load("sprites/pacman_full.png")
        self.current_sprite = pygame.transform.scale(pacman, (self.game.CELL_SIZE, self.game.CELL_SIZE))

    def eat_pellet(self, type, score, x, y):
        """ Eat a pellet of the given type ('small' or 'big'). """
        if type == 'small':
            self.game.small_pellets.remove((x, y))
        elif type == 'big':
            self.game.big_pellets.remove((x, y))
        self.game.score += score
        self.game.update_pellets_screen()

    def is_on_ghost(self):
        """ Check if Pacman is on a ghost. """
        for ghost in self.game.ghosts_pos:
            if self.hitbox.collidepoint(ghost[1]):

                if self.game.powered_up:
                    ghost[0].reset_position()
                else:
                    self.game.lives -= 1
                    if self.game.lives <= 0:
                        self.game.running = False
                    self.game.reset_positions()
    
    def reset_position(self):
        """ Reset Pacman's position to the starting location. """
        self.x, self.y = (self.game.width // 2 - 2, self.game.height - 2)
        self.px = self.x * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
        self.py = self.y * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
        self.next_dir = (0, 0)


    def update(self):
        """ Update the pacman location. """
        move.get_direction(self, True)
        move.move(self)
        self.save += str(self.current_dir)
        self.hitbox = pygame.Rect(self.px, self.py, 0, 0)
        self.hitbox = self.hitbox.inflate(self.game.CELL_SIZE, self.game.CELL_SIZE)

        # If Pacman is on a pellet, eat it
        for pellet in self.game.small_pellets | self.game.big_pellets:
            if self.hitbox.collidepoint(pellet[0] * self.game.CELL_SIZE + self.game.CELL_SIZE // 2, pellet[1] * self.game.CELL_SIZE + self.game.CELL_SIZE // 2):
                if pellet in self.game.small_pellets:
                    self.eat_pellet('small', 10, pellet[0], pellet[1])
                else:
                    self.eat_pellet('big', 50, pellet[0], pellet[1])
                    # self.game.powered_up = True
                    self.game.power_up()
                break  # Exit loop after eating a pellet


        self.is_on_ghost()

        if not self.game.small_pellets and not self.game.big_pellets:
            self.game.win = True