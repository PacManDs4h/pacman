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

        cs = self.game.CELL_SIZE
        self.speed_px = self.MOVE_SPEED_CELLS_PER_SEC * cs

        # centre actuel de Pac-Man dans le monde pixel
        pac_center_x = self.pac_x * cs + cs / 2
        pac_center_y = self.pac_y * cs + cs / 2

        # savoir si Pac-Man est exactement au centre
        at_center = abs(self.pac_px - pac_center_x) < 0.1 and abs(self.pac_py - pac_center_y) < 0.1

        # Si Pac-Man est centré : gérer les changements de direction
        if at_center:

            # Réaligner pour éviter les erreurs de flottants
            self.pac_px = pac_center_x
            self.pac_py = pac_center_y

            # Le joueur veut tourner ?
            if self.next_dir != (0, 0):
                tx = (self.pac_x + self.next_dir[0])
                ty = (self.pac_y + self.next_dir[1])

                # Peut-on tourner ?
                if self.game.cell_free(tx, ty) and not self.game.is_ghost_house_door(tx, ty):
                    # On tourne
                    self.current_dir = self.next_dir
                    self.pacman_sprite = {(0, -1): self.pacman_up,
                            (0, 1): self.pacman_down,
                            (-1, 0): self.pacman_left,
                                (1, 0): self.pacman_right}[self.next_dir]
                else:
                    # Sinon, essayer de continuer tout droit
                    cx = self.pac_x + self.current_dir[0]
                    cy = self.pac_y + self.current_dir[1]
                    if not self.game.cell_free(cx, cy) or self.game.is_ghost_house_door(cx, cy):
                        self.current_dir = (0, 0)

            else:
                # Aucune direction, vérifier si continuer est possible
                cx = self.pac_x + self.current_dir[0]
                cy = self.pac_y + self.current_dir[1]
                if not self.game.cell_free(cx, cy) or self.game.is_ghost_house_door(cx, cy):
                    self.current_dir = (0, 0)

        # Déplacement (si une direction active existe)
        if self.current_dir != (0, 0):

            dx, dy = self.current_dir

            # mouvement voulu cette frame
            move_x = dx * self.speed_px * self.game.dt
            move_y = dy * self.speed_px * self.game.dt

            # prochaine cellule
            next_cell_x = (self.pac_x + dx) % self.game.width
            next_cell_y = (self.pac_y + dy) % self.game.height

            # centre de la prochaine cellule
            target_cx = next_cell_x * cs + cs / 2
            target_cy = next_cell_y * cs + cs / 2

            # distance à ce centre (en tenant compte du warp)
            dist_x = self.game.toroidal_delta(target_cx, self.pac_px, self.game.game_screen_w)
            dist_y = self.game.toroidal_delta(target_cy, self.pac_py, self.game.game_screen_h)

            # Est-ce qu'on dépasserait le centre ?
            overshoot_x = (dx != 0 and abs(move_x) >= abs(dist_x))
            overshoot_y = (dy != 0 and abs(move_y) >= abs(dist_y))

            if overshoot_x or overshoot_y:
                # On arrive exactement au centre de la prochaine case
                self.pac_px = target_cx % self.game.game_screen_w
                self.pac_py = target_cy % self.game.game_screen_h

                # mise à jour des coordonnées grille
                self.pac_x = next_cell_x
                self.pac_y = next_cell_y

            else:
                # Avancer normalement
                self.pac_px = (self.pac_px + move_x) % self.game.game_screen_w
                self.pac_py = (self.pac_py + move_y) % self.game.game_screen_h

        else:
            # Pac-Man ne bouge pas, rester centré
            self.pac_px = pac_center_x
            self.pac_py = pac_center_y

        # If Pacman is on a pellet, eat it
        if (self.pac_x, self.pac_y) in self.game.pellets:
            self.eat_pellet('small', 10, self.pac_x, self.pac_y)
        elif (self.pac_x, self.pac_y) in self.game.big_pellets:
            self.eat_pellet('big', 50, self.pac_x, self.pac_y)

        self.is_on_ghost()

        if not self.game.pellets and not self.game.big_pellets:
            self.game.win = True