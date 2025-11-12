import pygame 
from kaempfer import Kaempfer

pygame.init()

#Spielfenster erstellen
BILDSCHIRMBREITE = 1000
BILDSCHIRMHOEHE = 600

bildschirm = pygame.display.set_mode((BILDSCHIRMBREITE, BILDSCHIRMHOEHE))
pygame.display.set_caption('Clash of Shadows')

#Hintergrundbild laden 
hintergrundbild = pygame.image.load('Ressourcen/Bilder/Hintergrund/Hintergrundbild.png').convert_alpha()

#Funktion zum Zeichnen des Hintergrunds
def hintergrund_zeichnen():
    skalierter_hintergrund = pygame.transform.scale(hintergrundbild, (BILDSCHIRMBREITE, BILDSCHIRMHOEHE))
    bildschirm.blit(skalierter_hintergrund, (0, 0))


#Zwei Instanzen von Kämpfern erstellen 
kaempfer_1 = Kaempfer(200, 310)
kaempfer_2 = Kaempfer(700, 310)

#Spielschleife
laufen = True
while laufen:

    #Hintergrund zeichnen 
    hintergrund_zeichnen()

    #kaempfer zeichnen
    kaempfer_1.zeichnen(bildschirm)
    kaempfer_2.zeichnen(bildschirm)

    #Ereignisbehandler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            laufen = False


    #Anzeige aktualisieren 
    pygame.display.update()

#pygame verlassen 
pygame.quit()