
class pacman():
    """ This class represents the player. """
    def __init__(self, game):
        self.MOVE_SPEED_CELLS_PER_SEC = 15.0
        self.pac_x, self.pac_y = (game.width // 2 - 2, game.height - 2)

        # pixel position of Pacman's center (floats for smooth movement)
        self.pac_px = self.pac_x * game.CELL_SIZE + game.CELL_SIZE / 2
        self.pac_py = self.pac_y * game.CELL_SIZE + game.CELL_SIZE / 2

        # movement directions: current movement and next desired direction
        self.current_dir = (0, 0)
        self.next_dir = (0, 0)

        self.center_x = 0
        self.center_y = 0

        self.speed_px = 0

        self.move_x = 0
        self.move_y = 0

        self.target_cell_x = 0
        self.target_cell_y = 0

        self.target_cx = 0
        self.target_cy = 0
        
        self.dist_x = 0
        self.dist_y = 0

 
    def update(self):
        """ Update the player location. """
        pass