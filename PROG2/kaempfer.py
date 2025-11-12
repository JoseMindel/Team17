import pygame

class Kaempfer():
    def __init__(self, x, y):
        self.rechteck = pygame.Rect((x, y, 80, 180))


    def zeichnen(self, oberflaeche):
        pygame.draw.rect(oberflaeche, (255, 0, 0), self.rechteck)