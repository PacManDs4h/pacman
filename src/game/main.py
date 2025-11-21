import Game
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
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
    pygame.font.init()
 
    # Create our objects and set the data
    running = True
    clock = pygame.time.Clock()
 
    # Create an instance of the Game class
    game = Game.Game(screen)
 
    # Main game loop
    while running:
        
        # Pause for the next frame
        game.dt = clock.tick(60) / 1000.0

        # Process events (keystrokes, mouse clicks, etc)
        running = game.process_events()

        # Update object positions, check for collisions
        game.run_logic()
 
        # Draw the current frame
        game.display_frame()
 
    # Close window and exit
    pygame.quit()

if __name__ == "__main__":
    main()