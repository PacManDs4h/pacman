import json
from urllib.request import urlopen
import Game
import pygame
import Button
import Map
import threading
from urllib.request import Request, urlopen
import urllib.error

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 780

pygame.init()

size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Pacman")
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
pygame.font.init()
clock = pygame.time.Clock()

API_BASE_URL = "https://pacmaz-s1-o.onrender.com"

# Liste des options d'IA
AI_OPTIONS = ["blinky", "pinky", "inky", "clyde", "random"]


# Définition des couleurs pour l'affichage
COLORS = {
    "red": (255, 0, 0),
    "pink": (255, 182, 193),
    "blue": (0, 255, 255),
    "orange": (255, 165, 0),
    "blinky": (255, 0, 0),
    "pinky": (255, 182, 193),
    "inky": (0, 255, 255),
    "clyde": (255, 165, 0),
    "random": (200, 200, 200),
    "white": (255, 255, 255)
}

def get_next_ai(current_ai, direction=1):
    """ Passe à l'IA suivante (1) ou précédente (-1) """
    try:
        idx = AI_OPTIONS.index(current_ai)
    except ValueError:
        idx = 0
    
    new_idx = (idx + direction) % len(AI_OPTIONS)
    return AI_OPTIONS[new_idx]

def draw_text(surface, text, font, color, x, y, anchor="center"):
    """ 
    Helper pour dessiner du texte parfaitement aligné.
    x, y : Coordonnées du point d'ancrage
    anchor : 'center', 'midleft', 'midright', 'topleft', etc.
    """
    txt_obj = font.render(text, True, color)
    rect = txt_obj.get_rect()
    
    # Gestion des ancrages pour un centrage parfait
    if anchor == "center":
        rect.center = (x, y)
    elif anchor == "midleft":
        rect.midleft = (x, y)
    elif anchor == "midright":
        rect.midright = (x, y)
    elif anchor == "topleft":
        rect.topleft = (x, y)
    elif anchor == "topcenter":
        rect.midtop = (x, y)
        
    surface.blit(txt_obj, rect)
    return rect

def menu_ia_ghosts(screen):
    """ Affiche le menu de configuration des fantômes avec navigation flèches """
    running_menu = True
    
    # Configuration par défaut
    config = {
        "red": "blinky",
        "pink": "pinky",
        "blue": "inky",
        "orange": "clyde"
    }

    ghost_names = ["red", "pink", "blue", "orange"]

    # Fonts
    font_title = pygame.font.Font("fonts/emulogic.ttf", 40)
    font_item = pygame.font.Font("fonts/emulogic.ttf", 25)
    
    # Index de sélection (0-3: Fantômes, 4: Start)
    selected_idx = 0 
    
    # Bouton START
    # On le positionne un peu plus bas
    btn_start = Button.Button((SCREEN_WIDTH // 2, 680), "START GAME", (0, 255, 0), 40)
    
    while running_menu:
        clock.tick(60)
        screen.fill((0, 0, 0))
        
        # --- Affichage Titre ---
        draw_text(screen, "GHOST AI SETUP", font_title, (255, 255, 0), SCREEN_WIDTH // 2, 80, anchor="center")

        # --- Affichage des Lignes de Configuration ---
        start_y = 220
        row_height = 90 # Espace vertical entre les lignes
        
        for i, ghost_name in enumerate(ghost_names):
            current_ai = config[ghost_name]
            
            # Calcul du CENTRE VERTICAL de la ligne actuelle
            row_center_y = start_y + i * row_height
            
            # Couleurs
            ghost_color = COLORS.get(ghost_name, COLORS["white"])
            ai_color = COLORS.get(current_ai, COLORS["white"])
            
            # Textes
            str_ghost = f"{ghost_name.upper()} GHOST :"
            str_ai = f"{current_ai.upper()}"
            
            # Cadre de sélection et flèches
            if i == selected_idx:
                str_ai_display = f"< {str_ai} >"
                
                # Rectangle centré sur row_center_y
                rect_width = 800
                rect_height = 60
                selection_rect = pygame.Rect(0, 0, rect_width, rect_height)
                selection_rect.center = (SCREEN_WIDTH // 2, row_center_y)
                
                # Fond gris foncé + Contour couleur fantôme
                pygame.draw.rect(screen, (30, 30, 30), selection_rect)
                pygame.draw.rect(screen, ghost_color, selection_rect, 3)
            else:
                str_ai_display = str_ai

            # Dessin du texte (Aligné verticalement sur row_center_y)
            
            # 1. Nom du fantôme (à gauche du centre, aligné à droite)
            # midright = (x, y) -> le point milieu-droit du texte sera à ces coordonnées
            draw_text(screen, str_ghost, font_item, ghost_color, SCREEN_WIDTH // 2 - 20, row_center_y, anchor="midright")
            
            # 2. Nom de l'IA (à droite du centre, aligné à gauche)
            # midleft = (x, y) -> le point milieu-gauche du texte sera à ces coordonnées
            draw_text(screen, str_ai_display, font_item, ai_color, SCREEN_WIDTH // 2 + 20, row_center_y, anchor="midleft")

        # --- Affichage Bouton Start ---
        screen.blit(btn_start.final, (btn_start.x_pos, btn_start.y_pos))
        
        if selected_idx == 4:
             # Cadre autour de START
             # On recalcule un rect propre autour du bouton pour le feedback visuel
             # (Supposant que btn_start.final est une surface)
             btn_rect = pygame.Rect(btn_start.x_pos, btn_start.y_pos, btn_start.width, btn_start.height)
             pygame.draw.rect(screen, (255, 255, 255), btn_rect, 4)

        # --- Gestion des Événements ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    return None # Retour
                
                # Navigation HAUT / BAS
                elif event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % 5
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % 5
                
                # Modification Valeur GAUCHE / DROITE
                elif event.key == pygame.K_LEFT:
                    if selected_idx < 4:
                        ghost = ghost_names[selected_idx]
                        config[ghost] = get_next_ai(config[ghost], direction=-1)
                elif event.key == pygame.K_RIGHT:
                    if selected_idx < 4:
                        ghost = ghost_names[selected_idx]
                        config[ghost] = get_next_ai(config[ghost], direction=1)
                
                # Validation
                elif event.key == pygame.K_RETURN:
                    if selected_idx == 4: # START
                        return config
                    else:
                        selected_idx += 1

        pygame.display.flip()

    return config

def game(type="normal", maze_id = None, ghost_config=None):
    screen.fill((0, 0, 0))
    font = pygame.font.Font("fonts/emulogic.ttf", 50)
    final = font.render("Loading...", True, (255, 255, 255))
    screen.blit(final, (SCREEN_WIDTH // 2 - final.get_width() // 2, 350))
    pygame.display.flip()

    running = True

    # Create an instance of the Game class
    game = Game.Game(screen, type, maze_id, ghost_config=ghost_config)
 
    # Main game loop
    while running:
        game.dt = clock.tick(60) / 1000.0

        if type == "normal":
            running = game.process_events()
        elif type == "record":
            running = game.process_events()
        elif type == "play_save":
            running = game.process_save()

        game.run_logic()
        game.display_frame()

    if type == "record":
        with open("save.txt", "w") as f:
            f.write(game.id)
            f.write("#")
            f.write(game.pacman.save)
            
    # If this was a normal game, post the score asynchronously (silent on failure)
    if type == "normal":
        try:
            player_name = getattr(game, "player_name", None)
            print(f"DEBUG: end-of-game send attempt in game(): type={type!r}, game.type={getattr(game,'type',None)!r}, player_name={player_name!r}, score={getattr(game,'score',None)!r}")
            if player_name and isinstance(player_name, str):
                def _post():
                    try:
                        payload = json.dumps({
                            "player_name": player_name,
                            "score": game.score,
                            "maze_id": game.id
                        }).encode("utf-8")
                        req = Request(f"{API_BASE_URL}/score", data=payload, headers={"Content-Type": "application/json"})
                        urlopen(req, timeout=5)
                    except Exception:
                        # silent failure
                        return

                t = threading.Thread(target=_post, daemon=True)
                t.start()
        except Exception:
            pass

    if game.quit:
        pygame.quit()
    else:
        main_menu()

def play():
    running = True
    buttons = [
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3), "Normal", (255, 255, 255), 90),
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), "Record", (255, 255, 255), 90),
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5), "Play Save", (255, 255, 255), 90)
    ]

    max_index = len(buttons) - 1
    button_id = 0
    action = 0
    
    while running:
        clock.tick(60)
        screen.fill((0, 0, 0))
        for button in buttons:
            screen.blit(button.final, (button.x_pos, button.y_pos))
            
        bt = buttons[button_id]
        pygame.draw.rect(screen, (255, 255, 255), (bt.x_pos, bt.y_pos, bt.width, bt.height), width=3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if button_id == 0:
                        action = 1 # Normal
                    elif button_id == 1:
                        action = 2 # Record
                    elif button_id == 2:
                        action = 3 # Play Save
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    action = 0
                    running = False
                elif event.key == pygame.K_UP:
                    if button_id - 1 >= 0:
                        button_id -= 1
                elif event.key == pygame.K_DOWN:
                    if button_id + 1 <= max_index:
                        button_id += 1

        pygame.display.flip()

    if action == 0:
        main_menu()
    elif action == 1:
        # Prompt player name before starting a normal game
        player_name = get_player_name()
        if player_name is None:
            # cancelled, go back to menu
            main_menu()
        else:
            # start game and attach player_name to Game instance
            g = Game.Game(screen, "normal")
            g.player_name = player_name
            run_game_instance(g)
    elif action == 2:
        game("record")
        
    elif action == 1 or action == 3:
        mode_str = "normal" if action == 1 else "play_save"
        conf = menu_ia_ghosts(screen)
        
        if conf is not None:
            game(mode_str, ghost_config=conf)
        else:
            main_menu()

    if action not in [0, 1, 2, 3]:
        pygame.quit()


def maps():
    running = True
    font = pygame.font.Font("fonts/emulogic.ttf", 40)
    map_txt = font.render("Map list", True, (255, 255, 255))
    loading = font.render("Loading...", True, (255, 255, 255))

    action = 0
    screen.fill((0, 0, 0))
    screen.blit(map_txt, (SCREEN_WIDTH // 2 - map_txt.get_width() // 2, 20))
    screen.blit(loading, (SCREEN_WIDTH // 2 - loading.get_width() // 2, 350))
    pygame.display.flip()

    url = f"https://pacmaz-s1-o.onrender.com/mazes"
    response = urlopen(url)
    data_json = json.loads(response.read())
    
    mazes = data_json["mazes"]
    mazes_count = data_json["count"]

    maps = []
    n = 0

    for i in range(mazes_count):
        maze, width, height, maze_id = get_data(mazes[i])
        map = Map.Map(maze, width, height, 700, maze_id)
        maps.append(map)

    while running:
        clock.tick(60)
        screen.fill((0, 0, 0))
        screen.blit(maps[n].bg,(SCREEN_WIDTH // 2 - maps[n].bg.get_width() // 2, SCREEN_HEIGHT // 2 - maps[n].bg.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    action = 1
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    action = 0
                    running = False
                elif event.key == pygame.K_LEFT:
                    if n - 1 >= 0:
                        n -= 1
                elif event.key == pygame.K_RIGHT:
                    if n + 1 < mazes_count:
                        n += 1

        pygame.display.flip()
        
    if action == 0:
        main_menu()
    elif action == 1:
        game("normal", maps[n].maze_id)

    pygame.quit()

def get_data(maze):
    maze_id = maze["id"]
    width = maze["params"]["width"]
    height = maze["params"]["height"]
    url = f"https://pacmaz-s1-o.onrender.com/maze/{maze_id}"
    response = urlopen(url)
    data_json = json.loads(response.read())
    maze = data_json.get("maze")
    return maze, width, height, maze_id


def get_player_name():
    """Simple Pygame text input prompt. Returns the entered name (max 20 chars) or None if cancelled."""
    font = pygame.font.Font("fonts/emulogic.ttf", 40)
    prompt = font.render("Enter name (max 20 chars):", True, (255, 255, 255))
    name = ""
    running = True

    while running:
        clock.tick(30)
        screen.fill((0, 0, 0))
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 3))

        # render current name
        name_surf = font.render(name + ("|" if int(pygame.time.get_ticks() / 500) % 2 == 0 else ""), True, (200, 200, 200))
        screen.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, SCREEN_HEIGHT // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(name.strip()) == 0:
                        # require non-empty
                        continue
                    return name.strip()[:20]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return None
                else:
                    # limit to printable characters
                    ch = event.unicode
                    if ch and len(name) < 20 and (32 <= ord(ch) <= 126):
                        name += ch

        pygame.display.flip()


def run_game_instance(game_inst):
    """Run the main loop for an existing Game instance (used so we can attach player_name)."""
    # show loading
    screen.fill((0, 0, 0))
    font = pygame.font.Font("fonts/emulogic.ttf", 50)
    final = font.render("Loading...", True, (255, 255, 255))
    screen.blit(final,(SCREEN_WIDTH // 2 - final.get_width() // 2, 350))
    pygame.display.flip()

    # start the provided game instance main loop
    running = True
    game = game_inst

    # Main loop
    while running:
        game.dt = clock.tick(60) / 1000.0
        if game.type == "normal":
            running = game.process_events()
        elif game.type == "record":
            running = game.process_events()
        elif game.type == "play_save":
            running = game.process_save()

        game.run_logic()
        game.display_frame()

    # handle record save
    if game.type == "record":
        try:
            with open("save.txt", "w") as f:
                f.write(game.id)
                f.write("#")
                f.write(game.pacman.save)
        except Exception:
            pass

    # post score async if normal (do this BEFORE returning to the menu)
    if game.type == "normal":
        try:
            player_name = getattr(game, "player_name", None)
            if player_name and isinstance(player_name, str):
                def _post():
                    try:
                        payload = json.dumps({
                            "player_name": player_name,
                            "score": game.score,
                            "maze_id": game.id
                        }).encode("utf-8")
                        req = Request(f"{API_BASE_URL}/score", data=payload, headers={"Content-Type": "application/json"})
                        urlopen(req, timeout=5)
                    except Exception:
                        return

                t = threading.Thread(target=_post, daemon=True)
                t.start()
        except Exception:
            pass

    if game.quit:
        pygame.quit()
    else:
        main_menu()

def leaderboard():
    """Fetch top scores from the server and display them in a styled Pacman-themed screen."""
    running = True
    title_font = pygame.font.Font("fonts/emulogic.ttf", 60)
    entry_font = pygame.font.Font("fonts/emulogic.ttf", 30)
    small_font = pygame.font.Font("fonts/emulogic.ttf", 20)

    try:
        url = f"{API_BASE_URL}/leaderboard?limit=5"
        resp = urlopen(url, timeout=5)
        data_json = json.loads(resp.read())
        entries = data_json.get("leaderboard", [])
    except Exception as e:
        entries = []
        error_msg = f"Erreur chargement: {e}"

    while running:
        clock.tick(60)
        screen.fill((0, 0, 0))

        # Title
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 40))

        # Draw column headers
        header_x = SCREEN_WIDTH // 4
        draw_text(screen, "Rank", small_font, (255,255,255), header_x, 140, anchor="midleft")
        draw_text(screen, "Player", small_font, (255,255,255), header_x + 150, 140, anchor="midleft")
        draw_text(screen, "Score", small_font, (255,255,255), header_x + 450, 140, anchor="midleft")

        # Draw entries
        start_y = 180
        line_h = 48
        for i, e in enumerate(entries):
            rank = i + 1
            name = e.get("player_name", "---")
            score = e.get("score", 0)
            created = e.get("created_at")

            # Pacman colors for top ranks
            if rank == 1:
                color = (255, 215, 0)
            elif rank == 2:
                color = (192, 192, 192)
            elif rank == 3:
                color = (205, 127, 50)
            else:
                color = (200, 200, 200)

            draw_text(screen, f"#{rank}", entry_font, color, header_x, start_y + i * line_h, anchor="midleft")
            draw_text(screen, name, entry_font, (255,255,255), header_x + 150, start_y + i * line_h, anchor="midleft")
            draw_text(screen, str(score), entry_font, (255,255,255), header_x + 450, start_y + i * line_h, anchor="midleft")

        if not entries:
            # show error or empty
            msg = "Aucun score trouvé." if 'error_msg' not in locals() else error_msg
            draw_text(screen, msg, entry_font, (255, 100, 100), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Footer
        info = small_font.render("Press BACKSPACE to return", True, (200,200,200))
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, SCREEN_HEIGHT - 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()



def main_menu():
    running = True
    buttons = [
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3), "Play", (255, 255, 255), 90),
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.6), "Leaderboard", (255, 255, 255), 70),
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), "Maps", (255, 255, 255), 90),
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.2), "Quit", (255, 255, 255), 60)
    ]
    max_index = len(buttons) - 1
    button_id = 0

    action = 0

    while running:
        clock.tick(60)
        screen.fill((0, 0, 0))
        for button in buttons:
            screen.blit(button.final, (button.x_pos, button.y_pos))
            
        bt = buttons[button_id]
        pygame.draw.rect(screen, (255, 255, 255), (bt.x_pos, bt.y_pos, bt.width, bt.height), width=3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if button_id == 0:
                        action = 1
                        running = False
                    elif button_id == 1:
                        action = 2
                        running = False
                    elif button_id == 2:
                        running = False
                elif event.key == pygame.K_UP:
                    if button_id - 1 >= 0:
                        button_id -= 1
                elif event.key == pygame.K_DOWN:
                    if button_id + 1 <= max_index:
                        button_id += 1

        pygame.display.flip()

    if action == 1:
        play()
    elif action == 2:
        leaderboard()
    elif action == 3:
        maps()

    pygame.quit()

if __name__ == "__main__":
    main_menu()
