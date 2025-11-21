import pygame

class Pacman():
    """ This class represents the player. """
    def __init__(self, game):
        self.game = game
        
        self.MOVE_SPEED_CELLS_PER_SEC = 7.0
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
        self.load_sprites()

 
    def load_sprites(self):
        pacman = pygame.image.load("sprites/pacman_full.png")
        self.pacman_sprite = pygame.transform.scale(pacman, (self.game.CELL_SIZE, self.game.CELL_SIZE))
        pacman_right = pygame.image.load("sprites/pacman_right.png")

        self.pacman_right = pygame.transform.scale(pacman_right, (self.game.CELL_SIZE, self.game.CELL_SIZE))
        self.pacman_left = pygame.transform.flip(self.pacman_right, True, False)
        self.pacman_up = pygame.transform.rotate(self.pacman_right, 90)
        self.pacman_down = pygame.transform.flip(self.pacman_up, False, True)


    def eat_pellet(self, type, score, x, y):
        """ Eat a pellet of the given type ('small' or 'big'). """
        if type == 'small':
            if (x, y) in self.game.pellets:
                self.game.pellets.remove((x, y))
        elif type == 'big':
            if (x, y) in self.game.big_pellets:
                self.game.big_pellets.remove((x, y))
        self.game.score += score
        self.game.update_pellets_screen()

    def is_on_ghost(self):
        """ Check if Pacman is on a ghost. """
        if (self.pac_x, self.pac_y) == (self.game.red_ghost.ghost_x, self.game.red_ghost.ghost_y):
            self.game.lives -= 1
            if self.game.lives <= 0:
                self.game.running = False
            self.reset_position()
    
    def reset_position(self):
        """ Reset Pacman's position to the starting location. """
        self.pac_x, self.pac_y = (self.game.width // 2 - 2, self.game.height - 2)
        self.pac_px = self.pac_x * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
        self.pac_py = self.pac_y * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
        self.current_dir = (0, 0)
        self.next_dir = (0, 0)

    def update(self):
        """ Update the player location. """
        self.center_x = self.pac_x * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
        self.center_y = self.pac_y * self.game.CELL_SIZE + self.game.CELL_SIZE / 2

        # are we exactly (or close enough) at the center of current cell? (use toroidal distance)
        at_center = abs(self.game.toroidal_delta(self.pac_px, self.center_x, self.game.screen_w)) < 1e-6 and abs(self.game.toroidal_delta(self.pac_py, self.center_y, self.game.screen_h)) < 1e-6

        # if at center, we can change direction: prefer next_dir
        if at_center:
            # snap to exact center to avoid float drift
            self.pac_px = self.center_x
            self.pac_py = self.center_y
            # try to take the player's desired turn first
            if self.next_dir != (0, 0):
                tx, ty = self.pac_x + self.next_dir[0], self.pac_y + self.next_dir[1]
                # block entering the ghost house through the door for Pacman
                if self.game.cell_free(tx, ty) and not self.game.is_ghost_house_door(tx, ty):
                    self.current_dir = self.next_dir
                    self.pacman_sprite = {(0, -1): self.pacman_up,
                            (0, 1): self.pacman_down,
                            (-1, 0): self.pacman_left,
                                (1, 0): self.pacman_right}[self.next_dir]
                else:
                    # if desired direction blocked, keep going current_dir if possible
                    cx, cy = self.pac_x + self.current_dir[0], self.pac_y + self.current_dir[1]
                    # also prevent continuing into the ghost house door
                    if not self.game.cell_free(cx, cy) or self.game.is_ghost_house_door(cx, cy):
                        self.current_dir = (0, 0)
            else:
                # no next direction requested: check if current_dir still possible
                cx, cy = self.pac_x + self.current_dir[0], self.pac_y + self.current_dir[1]
                # also prevent continuing into the ghost house door
                if not self.game.cell_free(cx, cy) or self.game.is_ghost_house_door(cx, cy):
                    self.current_dir = (0, 0)

        # move along current_dir if allowed
        if self.current_dir != (0, 0):
            self.speed_px = self.MOVE_SPEED_CELLS_PER_SEC * self.game.CELL_SIZE
            # desired movement in pixels this frame
            self.move_x = self.current_dir[0] * self.speed_px * self.game.dt
            self.move_y = self.current_dir[1] * self.speed_px * self.game.dt

            # compute target cell (wrapped) and its center for the next cell in movement direction
            self.target_cell_x = (self.pac_x + self.current_dir[0]) % self.game.width
            self.target_cell_y = (self.pac_y + self.current_dir[1]) % self.game.height
            self.target_cx = self.target_cell_x * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
            self.target_cy = self.target_cell_y * self.game.CELL_SIZE + self.game.CELL_SIZE / 2

            # distance remaining to the target center (use toroidal minimal distance)
            self.dist_x = self.game.toroidal_delta(self.target_cx, self.pac_px, self.game.screen_w)
            self.dist_y = self.game.toroidal_delta(self.target_cy, self.pac_py, self.game.screen_h)

            # if movement in this frame would overshoot the target center, snap to center and update grid cell
            if (abs(self.move_x) >= abs(self.dist_x) and self.current_dir[0] != 0) or (abs(self.move_y) >= abs(self.dist_y) and self.current_dir[1] != 0):
                # snap to target center (and wrap grid coords)
                self.pac_px = self.target_cx % self.game.screen_w
                self.pac_py = self.target_cy % self.game.screen_h
                self.pac_x = (self.pac_x + self.current_dir[0]) % self.game.width
                self.pac_y = (self.pac_y + self.current_dir[1]) % self.game.height
                # after arriving, allow immediate turn in the same frame on next loop iteration
            else:
                self.pac_px += self.move_x
                self.pac_py += self.move_y
                # keep pixel position wrapped so drawing stays on-screen
                self.pac_px %= self.game.screen_w
                self.pac_py %= self.game.screen_h
        else:
            # not moving: keep pac centered on its grid cell (avoid drift)
            self.pac_px = self.pac_x * self.game.CELL_SIZE + self.game.CELL_SIZE / 2
            self.pac_py = self.pac_y * self.game.CELL_SIZE + self.game.CELL_SIZE / 2

        # If Pacman is on a pellet, eat it
        if (self.pac_x, self.pac_y) in self.game.pellets:
            self.eat_pellet('small', 10, self.pac_x, self.pac_y)
        elif (self.pac_x, self.pac_y) in self.game.big_pellets:
            self.eat_pellet('big', 50, self.pac_x, self.pac_y)

        self.is_on_ghost()

        if not self.game.pellets and not self.game.big_pellets:
            self.game.win = True