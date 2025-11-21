import pygame

class Ghost():
    """ This class represents a ghost. """
    def __init__(self, game, color, start_x, start_y):
        self.game = game
        self.color = color
        self.start_x = start_x
        self.start_y = start_y

        self.MOVE_SPEED_CELLS_PER_SEC = 15.0
    
        self.ghost_x = start_x
        self.ghost_y = start_y
        self.load_sprites()
    

    def load_sprites(self):
        if self.color == "red":
            ghost_image = pygame.image.load("sprites/red_ghost_left1.png")
            self.ghost_sprite = pygame.transform.scale(ghost_image, (self.game.CELL_SIZE, self.game.CELL_SIZE)).convert()
        # Additional colors can be added here
    
    def update(self):
        """ Update the ghost location. """
        # For now, the ghost just stays still at its starting position
        self.ghost_pos = (self.ghost_x * self.game.CELL_SIZE, self.ghost_y * self.game.CELL_SIZE)
        pass