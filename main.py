import pygame 
from kaempfer import Kaempfer

pygame.init()

#Spielfenster erstellen
bildschirmbreite = 1000
bildschirmhoehe = 600

bildschirm = pygame.display.set_mode((bildschirmbreite, bildschirmhoehe))
pygame.display.set_caption('Clash of Shadows')

#Bildrate einstellen
uhr = pygame.time.Clock()
FPS = 60

#Hintergrundbild laden 
hintergrundbild = pygame.image.load('Ressourcen/Bilder/Hintergrund/Hintergrundbild.png').convert_alpha()

#Funktion zum Zeichnen des Hintergrunds
def hintergrund_zeichnen():
    skalierter_hintergrund = pygame.transform.scale(hintergrundbild, (bildschirmbreite, bildschirmhoehe))
    bildschirm.blit(skalierter_hintergrund, (0, 0))


#Zwei Instanzen von Kämpfern erstellen 
kaempfer_1 = Kaempfer(200, 310, 1)
kaempfer_2 = Kaempfer(700, 310, 2)

#Spielschleife
laufen = True
while laufen:

    uhr.tick(FPS)

#Ereignisbehandler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            laufen = False
    #Hintergrund zeichen 
    hintergrund_zeichnen()

    #Kämpfer bewegen
    kaempfer_1.bewegen(bildschirmbreite, bildschirmhoehe, bildschirm)
    kaempfer_2.bewegen(bildschirmbreite, bildschirmhoehe, bildschirm)

    #kaempfer zeichnen
    kaempfer_1.zeichnen(bildschirm)
    kaempfer_2.zeichnen(bildschirm)

#Ereignisbehandler
    """ for event in pygame.event.get():
        if event.type == pygame.QUIT:
            laufen = False """


    #Anzeige aktualisieren 
    pygame.display.update()

#pygame verlassen 
pygame.quit()