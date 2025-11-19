import pygame

class Kaempfer():
    def __init__(self, x, y):
        self.rechteck = pygame.Rect((x, y, 80, 180))


    def bewegen (self, bildschirmbreite):
        GESCHWINDIGKEIT = 10
        dx = 0
        dy = 0

        #Tasten erfassen 
        tasten = pygame.key.get_pressed()

        #bewegung
        if tasten[pygame.K_a]:
            dx = -GESCHWINDIGKEIT
        if tasten[pygame.K_d]:
            dx = GESCHWINDIGKEIT

        #sicherstellen, dass der Kämpfer im Bildschirm bleibt
        if self.rechteck.left + dx < 0:
            dx = -self.rechteck.left  
        if self.rechteck.right + dx > bildschirmbreite:
            dx = bildschirmbreite - self.rechteck.right

            #Spielerposition bearbeiten
            self.rechteck.x += dx
            self.rechteck.y += dy

    def zeichnen(self, oberflaeche):
        pygame.draw.rect(oberflaeche, (255, 0, 0), self.rechteck)