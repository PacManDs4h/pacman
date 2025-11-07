import random
import time

# Use these characters for displaying the maze:
EMPTY = ' '
MARK = '@'
WALL = chr(9608)  # Character 9608 is '█'
NORTH, SOUTH, EAST, WEST = 'n', 's', 'e', 'w'


class Maze:
    def __init__(self, width, height, nb_cycles, nb_wrap_tunnels, nb_center_tunnels):
        self.maze = {}
        self.width = width
        self.height = height
        self.nb_cycles = nb_cycles
        self.nb_wrap_tunnels = nb_wrap_tunnels
        self.nb_center_tunnels = nb_center_tunnels
        self.seed = None  # Pour stocker le seed utilisé comme ID
        # Ces attributs seront initialisés dans addHouse()
        self.corner_x = None
        self.corner_y = None

    def initialize_maze(self):
        """Initialize a filled-in maze data structure."""
        self.maze = {}  # Réinitialiser self.maze
        for x in range(self.width):
            for y in range(self.height):
                self.maze[(x, y)] = WALL  # Every space is a wall at first.

    def printMaze(self, markX=None, markY=None):
        """Displays the maze data structure."""
        for y in range(self.height):
            for x in range(self.width):
                if markX == x and markY == y:
                    print(MARK, end='')
                else:
                    print(self.maze[(x, y)], end='')
            print()

    def visit(self, x, y, hasVisited):
        """'Carve out' empty spaces in the maze at x, y and then
        recursively move to neighboring unvisited spaces."""
        self.maze[(x, y)] = EMPTY

        while True:
            unvisitedNeighbors = []
            if y > 1 and (x, y - 2) not in hasVisited:
                unvisitedNeighbors.append(NORTH)
            if y < self.height - 2 and (x, y + 2) not in hasVisited:
                unvisitedNeighbors.append(SOUTH)
            if x > 1 and (x - 2, y) not in hasVisited:
                unvisitedNeighbors.append(WEST)
            if x < self.width // 2 - 2 and (x + 2, y) not in hasVisited:
                unvisitedNeighbors.append(EAST)

            if len(unvisitedNeighbors) == 0:
                return
            else:
                nextIntersection = random.choice(unvisitedNeighbors)
                if nextIntersection == NORTH:
                    nextX, nextY = x, y - 2
                    self.maze[(x, y - 1)] = EMPTY
                elif nextIntersection == SOUTH:
                    nextX, nextY = x, y + 2
                    self.maze[(x, y + 1)] = EMPTY
                elif nextIntersection == WEST:
                    nextX, nextY = x - 2, y
                    self.maze[(x - 1, y)] = EMPTY
                elif nextIntersection == EAST:
                    nextX, nextY = x + 2, y
                    self.maze[(x + 1, y)] = EMPTY

                hasVisited.append((nextX, nextY))
                self.visit(nextX, nextY, hasVisited)

    def mirrorMaze(self):
        """Mirror the left half of the maze to the right to maintain width."""
        half = self.width // 2
        for x in range(half):
            for y in range(self.height):
                self.maze[(self.width - 1 - x, y)] = self.maze[(x, y)]

    def addCycles(self):
        """Add numCycles loops by randomly removing walls in the left half."""
        walls = [(x, y) for x in range(self.width // 2)
                 for y in range(self.height) if self.maze[(x, y)] == WALL]
        random.shuffle(walls)
        cyclesAdded = 0

        for x, y in walls:
            if cyclesAdded >= self.nb_cycles:
                break
            if (x > 0 and x < self.width // 2 - 1 and self.maze[(x - 1, y)] == EMPTY and self.maze[(x + 1, y)] == EMPTY):
                self.maze[(x, y)] = EMPTY
                cyclesAdded += 1
            elif (y > 0 and y < self.height - 1 and self.maze[(x, y - 1)] == EMPTY and self.maze[(x, y + 1)] == EMPTY):
                self.maze[(x, y)] = EMPTY
                cyclesAdded += 1

    def removeDeadEnds(self):
        """Remove dead-ends in the left half by connecting to adjacent corridors."""
        maxIterations = 100
        iterations = 0
        while iterations < maxIterations:
            deadEnds = []
            for x in range(1, self.width // 2):
                for y in range(1, self.height - 1):
                    if self.maze[(x, y)] == EMPTY:
                        wallsAround = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                                          if self.maze.get((x + dx, y + dy), WALL) == WALL)
                        if wallsAround == 3:
                            deadEnds.append((x, y))

            if not deadEnds:
                break

            x, y = random.choice(deadEnds)
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if self.maze.get((nx, ny), WALL) == WALL and 0 < nx < self.width // 2 and 0 < ny < self.height - 1:
                    if self.maze.get((nx + dx, ny + dy), WALL) == EMPTY:
                        self.maze[(nx, ny)] = EMPTY
                        break
            iterations += 1

    def addTunnels(self):
        """Add wrap-around tunnels at borders and independent center tunnels."""
        possible_y = list(range(1, self.height - 1, 2)
                          )  # Odd positions for alignment
        random.shuffle(possible_y)

        # Select y-positions for wrap-around tunnels
        wrap_y = possible_y[:min(self.nb_wrap_tunnels, len(possible_y))]

        # Select different y-positions for center tunnels
        remaining_y = [y for y in possible_y if y not in wrap_y]
        random.shuffle(remaining_y)
        center_y = remaining_y[:min(self.nb_center_tunnels, len(remaining_y))]

        # Add wrap-around tunnels at borders (left half and mirrored)
        for tunnelY in wrap_y:
            self.maze[(0, tunnelY)] = EMPTY
            self.maze[(1, tunnelY)] = EMPTY
            # Right side will be handled by mirrorMaze

        return center_y

    def applyCenterTunnels(self, center_y):
        """Apply center tunnels symmetrically."""
        center_x = self.width // 2
        for tunnelY in center_y:
            self.maze[(center_x, tunnelY)] = EMPTY
            if self.maze.get((center_x - 1, tunnelY), WALL) == WALL:
                self.maze[(center_x - 1, tunnelY)] = EMPTY
            if self.maze.get((center_x + 1, tunnelY), WALL) == WALL:
                self.maze[(center_x + 1, tunnelY)] = EMPTY

    def addHouse(self):
        """
        Ajoute la "maison" centrale.
        IMPORTANT: Stocke les coordonnées de la maison dans self.corner_x et self.corner_y
        pour que d'autres fonctions (comme le scoring) puissent les trouver.
        """
        pattern = [
            "EEEEEEE",
            "EWWEWWE",
            "EWEEEWE",
            "EWWWWWE",
            "EEEEEEE"
        ]

        # CHANGEMENT : Celles-ci sont maintenant des attributs (self.)
        self.corner_x = self.width // 2 - 3
        self.corner_y = self.height // 2 - 2

        for dy, row in enumerate(pattern):
            for dx, cell in enumerate(row):
                self.maze[(self.corner_x + dx, self.corner_y + dy)
                          ] = WALL if cell == 'W' else EMPTY
        # Coordonnées de la "porte" (le 'E' central sur la rangée du haut)
        door_x = self.corner_x + 3
        door_y = self.corner_y  # C'est la rangée du haut du pattern

        # Coordonnées de la cellule JUSTE AU-DESSUS de la porte
        cell_above_door_x = door_x
        cell_above_door_y = door_y - 1

        # Forcer cette cellule à être VIDE pour garantir une connexion.
        # On vérifie si elle est dans les limites, bien que ça devrait l'être.
        if cell_above_door_y > 0:
            self.maze[(cell_above_door_x, cell_above_door_y)] = EMPTY

    def checkSymmetry(self):
        """Check if the maze is symmetric around the central column."""
        half = self.width // 2
        for x in range(half):
            for y in range(self.height):
                if self.maze[(x, y)] != self.maze[(self.width - 1 - x, y)]:
                    # Correction de la f-string sur plusieurs lignes
                    print(
                        f"Asymmetry detected at ({x}, {y}) "
                        f"and ({self.width - 1 - x}, {y})"
                    )
                    return False
        return True

    def propConnexite(self):
        nb_cellules_empty = 0
        nb_cellules_wall = 0
        for x in range(self.width):
            for y in range(1, self.height - 1):  # Ignorer le haut et le bas
                if (self.maze[(x, y)] == ' '):
                    nb_cellules_empty += 1
                else:
                    nb_cellules_wall += 1

        if nb_cellules_empty == 0:  # Éviter la division par zéro
            return (0, nb_cellules_wall, 0)

        return (nb_cellules_empty, nb_cellules_wall, nb_cellules_wall / nb_cellules_empty)

    def generate_maze(self, seed=None):
        """Generate a Pacman-like maze with optional seed."""
        if seed is None:
            # Générer un seed basé sur l'heure
            self.seed = int(time.time() * 1000)
        else:
            self.seed = seed

        # Utiliser le seed pour la génération
        random.seed(self.seed)

        self.initialize_maze()  # Initialize maze correctly
        hasVisited = [(1, 1)]
        self.visit(1, 1, hasVisited)
        self.addCycles()
        self.removeDeadEnds()
        center_y = self.addTunnels()
        self.mirrorMaze()  # Apply symmetry after all modifications
        self.applyCenterTunnels(center_y)  # Add center tunnels symmetrically

        # addHouse est appelé, définissant self.corner_x et self.corner_y
        self.addHouse()

        if not self.checkSymmetry():
            print("Warning: Maze is not symmetric!")
        else:
            print("Symétrie: OK")
        return self.maze

    # --- NOUVELLES FONCTIONS POUR LA NOTATION ---

    def count_dead_ends(self):
        """Compte le nombre total de culs-de-sac dans le labyrinthe."""
        deadEnds = 0
        # Parcourir tout le labyrinthe, pas seulement la moitié
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.maze[(x, y)] == EMPTY:
                    wallsAround = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                                      if self.maze.get((x + dx, y + dy), WALL) == WALL)
                    if wallsAround == 3:
                        deadEnds += 1
        return deadEnds

    def check_house_accessibility(self):
        """Vérifie si la "porte" de la maison est bien ouverte sur un couloir."""

        # S'assure que addHouse a bien été appelé
        if self.corner_x is None or self.corner_y is None:
            print("Erreur: check_house_accessibility() appelée avant addHouse()")
            return False

        # Coordonnées de la "porte" (basées sur addHouse)
        door_x = self.corner_x + 3
        door_y = self.corner_y  # C'est "EEEEEEE", donc la porte est au-dessus

        # Coordonnée de la cellule juste au-dessus de la porte
        cell_above_door_x = door_x
        cell_above_door_y = door_y - 1

        # Vérifier si la porte est EMPTY (elle devrait l'être)
        # ET si la cellule au-dessus est EMPTY (connectée au reste)
        is_door_open = self.maze.get((door_x, door_y), WALL) == EMPTY
        is_connected = self.maze.get(
            (cell_above_door_x, cell_above_door_y), WALL) == EMPTY

        return is_door_open and is_connected

    def get_maze_score(self):
        """Calcule un score de qualité pour le labyrinthe généré."""

        # --- 1. Score d'Ouverture (max 2 points) ---
        # Basé sur propConnexite. Un ratio murs/vides bas est bon.
        # Disons qu'un ratio idéal < 0.8
        empty_cells, wall_cells, ratio = self.propConnexite()

        # Normalisation du score de ratio:
        # Ratio 0.7 -> 2 pts
        # Ratio 1.0 -> 1 pt
        # Ratio 1.3 -> 0 pt
        openness_score = max(0, min(2, (1.3 - ratio) * (2 / 0.6)))

        # --- 2. Score de Fluidité (max 2 points) ---
        # Basé sur le nombre de culs-de-sac. Moins c'est mieux.
        total_cells = (self.width - 2) * (self.height - 2)
        dead_ends = self.count_dead_ends()
        dead_end_ratio = 0
        if total_cells > 0:
            dead_end_ratio = dead_ends / total_cells  # Pourcentage de culs-de-sac

        # Normalisation du score de fluidité:
        # Ratio 0% -> 2 pts
        # Ratio 5% -> 1 pt
        # Ratio 10% -> 0 pt
        fluidity_score = max(0, min(2, (0.10 - dead_end_ratio) * (2 / 0.10)))

        # --- 3. Score de Structure (max 1 point) ---
        # La maison est-elle accessible ?
        structure_score = 1 if self.check_house_accessibility() else 0

        # --- Score Total ---
        total_score = round(
            openness_score + fluidity_score + structure_score, 2)
        if total_score > 5.0:
            total_score = 5.0  # Plafonner à 5

        return {
            "id_seed": self.seed,
            "total_score_on_5": total_score,
            "details": {
                "openness_score": round(openness_score, 2),
                "fluidity_score": round(fluidity_score, 2),
                "structure_score": round(structure_score, 2),
                "wall_to_empty_ratio": round(ratio, 3),
                "dead_end_count": dead_ends,
                "house_accessible": self.check_house_accessibility()
            }
        }
