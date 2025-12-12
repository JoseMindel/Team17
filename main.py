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

# Boden (muss zu kaempfer.py passen)
BODEN_Y = bildschirmhoehe - 110
KAEmpfer_BOX_H = 220

#Farben definieren
rot = (255, 0, 0)
gelb = (255, 255, 0)
weiß = (255, 255, 255)

#Kämpfer Variablen definieren
warrior_size = 162
warrior_scale = 4
warrior_offset = [68, 45]
warrior_data = [warrior_size, warrior_scale, warrior_offset]
wizard_size = 250
wizard_scale = 3
wizard_offset = [112, 93]
wizard_data = [wizard_size, wizard_scale, wizard_offset]

#Musik laden (später)

#pygame.mixer.music.load('Ressourcen/Audio/Background Music.mp3')

#Hintergrundbild laden 
hintergrundbild = pygame.image.load('Ressourcen/Bilder/Hintergrund/Hintergrundbild.png').convert_alpha()

#Sprites für Kämpfer laden
warrior = pygame.image.load('Ressourcen/brawler_images/images/warrior/Sprites/warrior.png').convert_alpha()
wizard = pygame.image.load('Ressourcen/brawler_images/images/wizard/Sprites/wizard.png').convert_alpha()

# Animation-Daten: (sprite_sheet, frame_width, frame_height, frame_count)
warrior_schritte = [10, 8, 1, 7, 7, 3, 7]  # Anzahl der Frames für jede Animation
wizard_schritte = [8, 8, 1, 8, 8, 3, 7]  # Anzahl der Frames für jede Animation    


#Zwei Instanzen von Kämpfern erstellen
# Nutze die korrekten Animations-Schritt-Listen
spawn_y = BODEN_Y - KAEmpfer_BOX_H
kaempfer_1 = Kaempfer(300, spawn_y, 1, warrior_data, warrior, warrior_schritte)
kaempfer_2 = Kaempfer(700, spawn_y, 2, wizard_data, wizard, wizard_schritte)

#Funktion zum Zeichnen des Hintergrunds
def hintergrund_zeichnen(oberflaeche):
    skalierter_hintergrund = pygame.transform.scale(hintergrundbild, (bildschirmbreite, bildschirmhoehe))
    oberflaeche.blit(skalierter_hintergrund, (0, 0))

#Funktion zum Zeichnen des Gesundheitsbalkens des Kämpfers
def zeichen_gesundheitsbalken(gesundheit, x, y, oberflaeche):
    # sichere, ganzzahlige Werte und Clamp der Gesundheit
    health = max(0, min(100, int(gesundheit)))
    ratio = health / 100
    width = 400
    height = 30
    border = 2

    # Hintergrund / leerer Balken
    pygame.draw.rect(oberflaeche, rot, (x, y, width, height))
    # gefüllter Teil (aktueller Health)
    pygame.draw.rect(oberflaeche, gelb, (x, y, int(width * ratio), height))
    # dünner Rahmen als Umrandung (nur Kontur)
    pygame.draw.rect(oberflaeche, weiß, (x - border, y - border, width + border * 2, height + border * 2), border)
     

# Setze gegenseitige Gegner-Referenzen, damit Angriffe Kollisionen prüfen können
kaempfer_1.gegner = kaempfer_2
kaempfer_2.gegner = kaempfer_1

#Spielschleife
laufen = True
while laufen:

    uhr.tick(FPS)

#Ereignisbehandler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            laufen = False
    #Hintergrund zeichen 
    hintergrund_zeichnen(bildschirm)

    #Gesundheitsbalken zeigen 
    zeichen_gesundheitsbalken(kaempfer_1.gesundheit, 20, 20, bildschirm)
    zeichen_gesundheitsbalken(kaempfer_2.gesundheit, 580, 20, bildschirm)

    #Kämpfer bewegen (übergebe den gegner, damit sie sich richtig ausrichten)
    kaempfer_1.move(bildschirmbreite, bildschirmhoehe, bildschirm, kaempfer_2)
    kaempfer_2.move2(bildschirmbreite, bildschirmhoehe, bildschirm, kaempfer_1)

    #kaempfer zeichnen
    kaempfer_1.zeichnen(bildschirm)
    kaempfer_2.zeichnen(bildschirm)

    #Anzeige aktualisieren 
    pygame.display.update()

#pygame verlassen 
pygame.quit()
