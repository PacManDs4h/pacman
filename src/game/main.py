import Game
import pygame
import Button

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 780

pygame.init()

size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Pacman")
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
pygame.font.init()
clock = pygame.time.Clock()

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
        game("normal")
    elif action == 2:
        game("record")
    elif action == 3:
        game("play_save")

    pygame.quit()


def maps():
    running = True
    font = pygame.font.Font("fonts/emulogic.ttf", 40)
    final = font.render("Map list", True, (255, 255, 255))

    action = 0
    
    while running:
        clock.tick(60)
        screen.fill((0, 0, 0))
        screen.blit(final,(SCREEN_WIDTH // 2 - final.get_width() // 2, 20))

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