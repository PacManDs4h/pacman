import json
from urllib.request import urlopen
import Game
import pygame
import Button
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

def game(type = "normal"):
    screen.fill((0, 0, 0))
    font = pygame.font.Font("fonts/emulogic.ttf", 50)
    final = font.render("Loading...", True, (255, 255, 255))
    screen.blit(final,(SCREEN_WIDTH // 2 - final.get_width() // 2, 350))
    pygame.display.flip()

    running = True

    # Create an instance of the Game class
    game = Game.Game(screen, type)
 
    # Main game loop
    while running:
        
        # Pause for the next frame
        game.dt = clock.tick(60) / 1000.0

        # Process events (keystrokes, mouse clicks, etc)
        if type == "normal":
            running = game.process_events()
        elif type == "record":
            running = game.process_events()
        elif type == "play_save":
            running = game.process_save()

        # Update object positions, check for collisions
        game.run_logic()
 
        # Draw the current frame
        game.display_frame()

    if type == "record":
        with open("save.txt", "w") as f:
            f.write(game.id)
            f.write("#")
            f.write(game.pacman.save)
            
    if game.quit:
        pygame.quit()
    else:
        main_menu()

    # If this was a normal game, post the score asynchronously (silent on failure)
    if type == "normal":
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
                        # silent failure
                        return

                t = threading.Thread(target=_post, daemon=True)
                t.start()
        except Exception:
            pass

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
            screen.blit(button.final,(button.x_pos, button.y_pos))
            
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
                        action = 3
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
    elif action == 3:
        game("play_save")

    pygame.quit()


def maps():
    running = True
    font = pygame.font.Font("fonts/emulogic.ttf", 40)
    map = font.render("Map list", True, (255, 255, 255))
    loading = font.render("Loading...", True, (255, 255, 255))

    action = 0
    screen.fill((0, 0, 0))
    screen.blit(map,(SCREEN_WIDTH // 2 - map.get_width() // 2, 20))
    screen.blit(loading,(SCREEN_WIDTH // 2 - loading.get_width() // 2, 350))
    pygame.display.flip()

    url = f"https://pacmaz-s1-o.onrender.com/mazes"
    response = urlopen(url)
    data_json = json.loads(response.read())
    mazes = data_json["mazes"]

    buttons = []

    for i in range(5):
        buttons.append(Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60 * i), mazes[i]["id"], (255, 255, 255), 30))

    while running:
        clock.tick(60)
        screen.fill((0, 0, 0))
        screen.blit(map,(SCREEN_WIDTH // 2 - map.get_width() // 2, 20))

        for button in buttons:
            screen.blit(button.final,(button.x_pos, button.y_pos))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    action = 0
                    running = False

        pygame.display.flip()
    if action == 0:
        main_menu()

    pygame.quit()


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

    if game.quit:
        pygame.quit()
    else:
        main_menu()

    # post score async if normal
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


def main_menu():
    running = True
    buttons = [
        Button.Button((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3), "Play", (255, 255, 255), 90),
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
            screen.blit(button.final,(button.x_pos, button.y_pos))
            
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
        maps()

    pygame.quit()
    

main_menu()