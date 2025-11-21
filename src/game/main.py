import game2
import pygame

SCREEN_WIDTH = 608
SCREEN_HEIGHT = 736

def main():
    """ Main program function. """
    # Initialize Pygame and set up the window
    pygame.init()
 
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
 
    pygame.display.set_caption("Pacman")
    # pygame.mouse.set_visible(False)
 
    # Create our objects and set the data
    running = True
    clock = pygame.time.Clock()
 
    # Create an instance of the Game class
    game = game2.Game2(screen)

 
    # Main game loop
    while running:
    # while True:
 
        game.dt = clock.tick(60) / 1000.0
        # Process events (keystrokes, mouse clicks, etc)
        running = game.process_events()

        # Update object positions, check for collisions
        game.run_logic()
 
        # Draw the current frame
        game.display_frame()
 
        # Pause for the next frame
        clock.tick(60)
 
    # Close window and exit
    pygame.quit()

if __name__ == "__main__":
    main()