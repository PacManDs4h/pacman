import pygame
from SpriteStripAnim import SpriteStripAnim
import move
import random
import math

class Ghost():
    """ This class represents a ghost. """
    def __init__(self, game, color, start_x, start_y, ia_type="blinky"):
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
        self.ia_type = ia_type

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

    def get_target(self):
        """ Définit la case cible selon la personnalité du fantôme """
        
        # On récupère les infos de Pacman
        pacman = self.game.pacman
        px, py = int(pacman.x), int(pacman.y)
        
        # On essaie de récupérer la direction de Pacman (sinon par défaut (0,0))
        p_dir_x, p_dir_y = getattr(pacman, 'next_dir', (0, 0)) 

        # IA Random
        if self.ia_type == "random":
            return None

        # IA Blinky (Chasseur directe)
        if self.ia_type == "blinky":
            return (px, py)

        # IA Pinky (Vise 4 cases devant)
        elif self.ia_type == "pinky":
            target_x = px + (p_dir_x * 4)
            target_y = py + (p_dir_y * 4)
            return (int(target_x), int(target_y))

        # IA Inky (Symétrie par rapport à Blinky)
        elif self.ia_type == "inky":
            # Il a besoin de la position de Blinky (Red)
            if hasattr(self.game, 'red_ghost'):
                red = self.game.red_ghost
                rx, ry = int(red.x), int(red.y)
                
                # Point pivot : 2 cases devant Pacman
                pivot_x = px + (p_dir_x * 2)
                pivot_y = py + (p_dir_y * 2)
                
                # Vecteur Blinky -> Pivot
                vec_x = pivot_x - rx
                vec_y = pivot_y - ry
                
                # Cible = Pivot + Vecteur (Double la distance)
                return (int(pivot_x + vec_x), int(pivot_y + vec_y))
            else:
                return (px, py) # Fallback sur comportement rouge

        # IA Clyde (retourne au coin gauche quand se rapproche de Pacman
        elif self.ia_type == "clyde":
            # Calcul de la distance avec Pacman (Euclidienne)
            gx, gy = int(self.x), int(self.y)
            distance = math.sqrt((gx - px)**2 + (gy - py)**2)
            
            if distance > 8:
                # Si loin : il chasse
                return (px, py)
            else:
                # Si trop près : il fuit vers son coin (ex: 0, Hauteur max)
                return (0, self.game.height - 1)

        # Par défaut (si autre couleur)
        return (px, py)

    def mouv_ghost(self):
        start_pos = (int(self.x), int(self.y))

        if self.ia_type == "random":
            self.next_dir = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
            if self.next_dir == (-self.current_dir[0], -self.current_dir[1]):
                self.next_dir = self.current_dir
            move.get_direction(self, True) # True = Random allowed inside move logic if implemented
            move.move(self)
            return
        
        target_pos = self.get_target()
        
        path = self.game.get_path_bfs(start_pos, target_pos)
        
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





