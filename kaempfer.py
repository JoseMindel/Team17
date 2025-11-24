import pygame

class Kaempfer():
    def __init__(self, x, y):
        self.rechteck = pygame.Rect((x, y, 80, 180))
        self.geschwindigkeit_y = 0
        self.springen = False


    def bewegen (self, bildschirmbreite, bildschirmhoehe):
        GESCHWINDIGKEIT = 10
        SCHWERKRAFT = 2
        dx = 0
        dy = 0

        #Tasten erfassen, mit Hilfe von ChatGPT Code für Tastenabfrage generiert
        tasten = pygame.key.get_pressed()

        #bewegung
        if tasten[pygame.K_a]:
            dx = -GESCHWINDIGKEIT
        if tasten[pygame.K_d]:
            dx = GESCHWINDIGKEIT
        #Sprung
        if tasten[pygame.K_w] and not self.springen == False:
            self.geschwindigkeit_y = -30
            self.springen = True

        #Schwerkraft anwenden
        self.geschwindigkeit_y += SCHWERKRAFT
        dy += self.geschwindigkeit_y

        #sicherstellen, dass der Kämpfer im Bildschirm bleibt
        if self.rechteck.left + dx < 0:
            dx = -self.rechteck.left  
        if self.rechteck.right + dx > bildschirmbreite:
            dx = bildschirmbreite - self.rechteck.right
            if self.rechteck.bottom + dy > bildschirmhoehe - 110:
                self.geschwindigkeit_y = 0
                self.springen = False
                dy = bildschirmhoehe - 110 - self.rechteck.bottom

            #Spielerposition bearbeiten
            self.rechteck.x += dx
            self.rechteck.y += dy

    def zeichnen(self, oberflaeche):
        pygame.draw.rect(oberflaeche, (255, 0, 0), self.rechteck)