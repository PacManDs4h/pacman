import pygame

class Button():
    "position, text, color, size"
    def __init__(self, pos, text, color, size):
        self.text = text
        self.font = pygame.font.Font("fonts/emulogic.ttf", size)
        self.final = self.font.render(self.text, True, color)
        self.width = self.final.get_width() + 10
        self.height = self.final.get_height()
        self.x_pos = pos[0] - self.width // 2
        self.y_pos = pos[1] - self.height // 2

