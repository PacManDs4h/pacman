def get_direction(self, pacman):
    cs = self.game.CELL_SIZE
    self.speed_px = self.MOVE_SPEED_CELLS_PER_SEC * cs

    # centre actuel dans le monde pixel
    self.center_x = self.x * cs + cs / 2
    self.center_y = self.y * cs + cs / 2

    # savoir exactement au centre
    at_center = abs(self.px - self.center_x) < 0.1 and abs(self.py - self.center_y) < 0.1
    # si centré : gérer les changements de direction
    if at_center:

        # réaligner pour éviter les erreurs de flottants
        self.px = self.center_x
        self.py = self.center_y

        # veut tourner ?
        if self.next_dir != (0, 0):
            tx = (self.x + self.next_dir[0])
            ty = (self.y + self.next_dir[1])

            # peut-on tourner ?
            if self.game.cell_free(tx, ty) and (not pacman or not self.game.is_ghost_house_door(tx, ty)):
                # on tourne
                self.current_dir = self.next_dir
                self.n = {(0, -1): 1,
                        (0, 1): 3,
                        (-1, 0): 2,
                            (1, 0): 0}[self.next_dir]

        cx = self.x + self.current_dir[0]
        cy = self.y + self.current_dir[1]
        if not self.game.cell_free(cx, cy) or (pacman and self.game.is_ghost_house_door(cx, cy)):
            self.current_dir = (0, 0)

def move(self, pacman):
    """ Function to move used by pacman and ghosts. """
    cs = self.game.CELL_SIZE
    if self.current_dir != (0, 0):

        dx, dy = self.current_dir

        # mouvement voulu cette frame
        move_x = dx * self.speed_px * self.game.dt
        move_y = dy * self.speed_px * self.game.dt

        # prochaine cellule
        next_cell_x = (self.x + dx) % self.game.width
        next_cell_y = (self.y + dy) % self.game.height

        # centre de la prochaine cellule
        target_cx = next_cell_x * cs + cs / 2
        target_cy = next_cell_y * cs + cs / 2

        # distance à ce centre (en tenant compte du warp)
        dist_x = self.game.toroidal_delta(target_cx, self.px, self.game.game_screen_w)
        dist_y = self.game.toroidal_delta(target_cy, self.py, self.game.game_screen_h)

        # Est-ce qu'on dépasserait le centre ?
        overshoot = abs(move_x if dx else move_y) >= abs(dist_x if dx else dist_y)

        if overshoot:
            # On arrive exactement au centre de la prochaine case
            self.px = target_cx % self.game.game_screen_w
            self.py = target_cy % self.game.game_screen_h

            # mise à jour des coordonnées grille
            self.x = next_cell_x
            self.y = next_cell_y

        else:
            # Avancer normalement
            self.px = (self.px + move_x) % self.game.game_screen_w
            self.py = (self.py + move_y) % self.game.game_screen_h
            self.current_sprite = self.strips[self.n].next()

    else:
        # ne bouge pas, rester centré
        self.px = self.center_x
        self.py = self.center_y
    
    self.center = self.px - cs // 2, self.py - cs // 2