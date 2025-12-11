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

#Farben definieren
rot = (255, 0, 0)
gelb = (255, 255, 0)
weiß = (255, 255, 255)

#Kämpfer Variablen definieren
kaempfer_1_größe = 64
kaempfer_1_daten = [kaempfer_1_größe] * 1  # Nur IDLE Animation für jetzt

#Hintergrundbild laden 
hintergrundbild = pygame.image.load('Ressourcen/Bilder/Hintergrund/Hintergrundbild.png').convert_alpha()

#Sprite-Blatt laden (optional)
try:
    sprite_sheet = pygame.image.load('Ressourcen/Bilder/Kaempfer_sprite.png').convert_alpha()
    # animation_schritte: [frames_idle, frames_walk, frames_attack, ...] (Anzahl Frames pro Reihe)
    animation_frames = [4, 6, 8]  # Beispiel: 4 idle, 6 walk, 8 attack (ANPASSEN!)
except:
    sprite_sheet = None
    animation_frames = None

#Spreete für Kämpfer laden
kaempfer_sprite_idle = pygame.image.load('Ressourcen/kaempfer_1/Sprites/IDLE.png').convert_alpha()
kaempfer_sprite_attack = pygame.image.load('Ressourcen/kaempfer_1/Sprites/ATTACK 1.png').convert_alpha()
kaempfer_sprite_hurt = pygame.image.load('Ressourcen/kaempfer_1/Sprites/HURT.png').convert_alpha()
kaempfer_sprite_run = pygame.image.load('Ressourcen/kaempfer_1/Sprites/RUN.png').convert_alpha()

# Animation-Daten: (sprite_sheet, frame_width, frame_height, frame_count)
# Index: 0=IDLE, 1=RUN, 2=ATTACK, 3=HURT
animation_data = [
    (kaempfer_sprite_idle, 96, 96, 9),      # IDLE
    (kaempfer_sprite_run, 110, 96, 14),     # RUN
    (kaempfer_sprite_attack, 84, 96, 8),    # ATTACK
    (kaempfer_sprite_hurt, 96, 96, 4),      # HURT
]

#Definieren Sie die Anzahl der Schritte in jeder Animation
Animation_Schritte = [ 
    9,  # IDLE - 9 frames
]

#Zwei Instanzen von Kämpfern erstellen 
kaempfer_1 = Kaempfer(200, 310, 1, sprite_datei=kaempfer_sprite_idle, animation_schritte=Animation_Schritte, frame_size=96, animation_data=animation_data)
kaempfer_2 = Kaempfer(700, 310, 2, sprite_datei=kaempfer_sprite_idle, animation_schritte=Animation_Schritte, frame_size=96, animation_data=animation_data)

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
    kaempfer_1.bewegen(bildschirmbreite, bildschirmhoehe, bildschirm, kaempfer_2)
    kaempfer_2.bewegen(bildschirmbreite, bildschirmhoehe, bildschirm, kaempfer_1)

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