import pygame
import os
from kaempfer import Kaempfer

pygame.init()


# Grundeinstellungen
bildschirmbreite = 1000
bildschirmhoehe = 600
bildschirm = pygame.display.set_mode((bildschirmbreite, bildschirmhoehe))
pygame.display.set_caption("Clash of Shadows")

uhr = pygame.time.Clock()
FPS = 60

BODEN_Y = bildschirmhoehe - 110
KAEmpfer_BOX_H = 220
spawn_y = BODEN_Y - KAEmpfer_BOX_H

# Farben
weiß = (255, 255, 255)
grau = (130, 130, 130)
rot = (255, 0, 0)
gelb = (255, 255, 0)
gruen = (0, 200, 0)
dunkelgrau = (30, 30, 30)

font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 72)


# Hintergrund
hintergrundbild = pygame.image.load(
    "Ressourcen/Bilder/Hintergrund/Hintergrundbild.png"
).convert_alpha()

def hintergrund_zeichnen():
    bild = pygame.transform.scale(
        hintergrundbild, (bildschirmbreite, bildschirmhoehe)
    )
    bildschirm.blit(bild, (0, 0))


# Menü
def farbe_fuer_hp(hp):
    if hp > 60:
        return gruen
    if hp > 30:
        return gelb
    return rot

def zeichne_gesundheitsbalken(hp, x, y):
    hp = max(0, min(100, int(hp)))
    ratio = hp / 100
    farbe = farbe_fuer_hp(hp)

    # dunkler Hintergrund, damit rot sichtbar bleibt
    pygame.draw.rect(bildschirm, dunkelgrau, (x, y, 400, 30))
    pygame.draw.rect(bildschirm, farbe, (x, y, int(400 * ratio), 30))
    pygame.draw.rect(bildschirm, weiß, (x - 2, y - 2, 404, 34), 2)

def zeichne_name(name, x, y):
    t = font.render(name, True, weiß)
    bildschirm.blit(t, (x, y))

def zeichne_runden_kreise(siege, x, y):
    radius = 8
    abstand = 22
    for i in range(2):
        pos = (x + i * abstand, y)
        if siege > i:
            pygame.draw.circle(bildschirm, weiß, pos, radius)
        else:
            pygame.draw.circle(bildschirm, weiß, pos, radius, 2)


# Hilfsfunktionen für Samurai
def finde_datei(ordner, namen):
    for n in namen:
        p = os.path.join(ordner, n)
        if os.path.exists(p):
            return p
    return None

def lade_sheet(pfad, frames, scale):
    bild = pygame.image.load(pfad).convert_alpha()
    frame_groesse = bild.get_height()
    liste = []
    for i in range(frames):
        frame = bild.subsurface(
            (i * frame_groesse, 0, frame_groesse, frame_groesse)
        )
        frame = pygame.transform.scale(
            frame, (frame_groesse * scale, frame_groesse * scale)
        )
        liste.append(frame)
    return liste, frame_groesse

def lade_samurai(ordner, frames, scale, offset):
    animationen = [[] for _ in range(7)]
    frame_groesse = 64

    idle = finde_datei(ordner, ["Idle (1).png", "Idle.png"])
    run = finde_datei(ordner, ["Run (1).png", "Run.png"])
    jump = finde_datei(ordner, ["Jump (1).png", "Jump.png"])
    attack = finde_datei(ordner, ["Attack1 (1).png", "Attack1.png"])
    hit = finde_datei(ordner, ["Take hit (1).png", "Take hit.png"])
    death = finde_datei(ordner, ["Death (1).png", "Death.png"])

    if idle:
        animationen[0], frame_groesse = lade_sheet(idle, frames["idle"], scale)
    if run:
        animationen[1], _ = lade_sheet(run, frames["run"], scale)
    if jump:
        animationen[2], _ = lade_sheet(jump, frames["jump"], scale)
    if attack:
        animationen[3], _ = lade_sheet(attack, frames["attack"], scale)
    if hit:
        animationen[4], _ = lade_sheet(hit, frames["hit"], scale)

    animationen[5] = animationen[0]

    if death:
        animationen[6], _ = lade_sheet(death, frames["death"], scale)

    daten = [frame_groesse, scale, offset]
    return animationen, daten


# Charakterdaten
warrior_sheet = pygame.image.load(
    "Ressourcen/brawler_images/images/warrior/Sprites/warrior.png"
).convert_alpha()

wizard_sheet = pygame.image.load(
    "Ressourcen/brawler_images/images/wizard/Sprites/wizard.png"
).convert_alpha()

charaktere = [
    {
        "name": "Warrior",
        "typ": "sheet",
        "sheet": warrior_sheet,
        "steps": [10, 8, 1, 7, 7, 3, 7],
        "data": [162, 4, [68, 45]],
    },
    {
        "name": "Wizard",
        "typ": "sheet",
        "sheet": wizard_sheet,
        "steps": [8, 8, 1, 8, 8, 3, 7],
        "data": [250, 3, [112, 93]],
    },
    {
        "name": "Samurai 1",
        "typ": "samurai",
        "ordner": "Ressourcen/samurai 1",
        "frames": {"idle": 4, "run": 8, "jump": 2, "attack": 4, "hit": 3, "death": 7},
        "scale": 3,
        # Positionsbestimmung
        "offset": [85, 53]
    },
    {
        "name": "Samurai 2",
        "typ": "samurai",
        "ordner": "Ressourcen/samurai 2",
        "frames": {"idle": 8, "run": 8, "jump": 2, "attack": 6, "hit": 3, "death": 6},
        "scale": 3,
        "offset": [85, 48]
    },
]


# Spielzustand
modus = "auswahl"
auswahl_links = 0
auswahl_rechts = 1

runde = 1
siege_links = 0
siege_rechts = 0

round_start = pygame.time.get_ticks()
round_time = 99
runde_beendet = False
pause_start = 0

kaempfer_links = None
kaempfer_rechts = None
name_links = ""
name_rechts = ""


# Kämpfer erzeugen
def erstelle_kaempfer(index, x, spieler_nr):
    c = charaktere[index]
    if c["typ"] == "sheet":
        return Kaempfer(x, spawn_y, spieler_nr, c["data"], c["sheet"], c["steps"])

    animationen, daten = lade_samurai(
        c["ordner"], c["frames"], c["scale"], c["offset"]
    )

    k = Kaempfer(x, spawn_y, spieler_nr, daten, None, [])
    k.animations_liste = animationen
    k.bild = animationen[0][0]
    return k


# Hauptschleife
laufen = True
while laufen:
    uhr.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            laufen = False

    hintergrund_zeichnen()

    if modus == "auswahl":
        titel = big_font.render("Charakter auswählen", True, weiß)
        bildschirm.blit(titel, (bildschirmbreite // 2 - 220, 50))

        t = pygame.key.get_pressed()

        if t[pygame.K_w]:
            auswahl_links = (auswahl_links - 1) % len(charaktere)
            pygame.time.delay(150)
        if t[pygame.K_s]:
            auswahl_links = (auswahl_links + 1) % len(charaktere)
            pygame.time.delay(150)

        if t[pygame.K_UP]:
            auswahl_rechts = (auswahl_rechts - 1) % len(charaktere)
            pygame.time.delay(150)
        if t[pygame.K_DOWN]:
            auswahl_rechts = (auswahl_rechts + 1) % len(charaktere)
            pygame.time.delay(150)

        for i, c in enumerate(charaktere):
            y = 160 + i * 40

            if i == auswahl_links:
                pygame.draw.rect(bildschirm, weiß, (200, y, 220, 35), 2)
            if i == auswahl_rechts:
                pygame.draw.rect(bildschirm, weiß, (580, y, 220, 35), 2)

            farbe_l = grau if i == auswahl_rechts else weiß
            farbe_r = grau if i == auswahl_links else weiß

            bildschirm.blit(font.render(c["name"], True, farbe_l), (220, y + 6))
            bildschirm.blit(font.render(c["name"], True, farbe_r), (600, y + 6))

        if t[pygame.K_RETURN] and auswahl_links != auswahl_rechts:
            name_links = charaktere[auswahl_links]["name"]
            name_rechts = charaktere[auswahl_rechts]["name"]

            kaempfer_links = erstelle_kaempfer(auswahl_links, 300, 1)
            kaempfer_rechts = erstelle_kaempfer(auswahl_rechts, 700, 2)

            kaempfer_links.gegner = kaempfer_rechts
            kaempfer_rechts.gegner = kaempfer_links

            modus = "kampf"
            round_start = pygame.time.get_ticks()
            runde_beendet = False

    else:
        sek = (pygame.time.get_ticks() - round_start) // 1000
        if not runde_beendet:
            round_time = max(0, 99 - sek)

        zeichne_gesundheitsbalken(kaempfer_links.gesundheit, 20, 20)
        zeichne_gesundheitsbalken(kaempfer_rechts.gesundheit, 580, 20)

        zeichne_name(name_links, 20, 55)
        zeichne_name(name_rechts, 580, 55)

        zeichne_runden_kreise(siege_links, 180, 67)
        zeichne_runden_kreise(siege_rechts, 740, 67)

        if not runde_beendet:
            kaempfer_links.move(bildschirmbreite, bildschirmhoehe, bildschirm, kaempfer_rechts)
            kaempfer_rechts.move2(bildschirmbreite, bildschirmhoehe, bildschirm, kaempfer_links)
        else:
            kaempfer_links._aktualisiere_frame()
            kaempfer_rechts._aktualisiere_frame()

        # Grundrichtung
        if kaempfer_links.rechteck.centerx < kaempfer_rechts.rechteck.centerx:
            kaempfer_links.umdrehen = False
            kaempfer_rechts.umdrehen = True
        else:
            kaempfer_links.umdrehen = True
            kaempfer_rechts.umdrehen = False

        # Samurai 1 bewusst invertieren
        if name_links == "Samurai 1":
            kaempfer_links.umdrehen = not kaempfer_links.umdrehen
        if name_rechts == "Samurai 1":
            kaempfer_rechts.umdrehen = not kaempfer_rechts.umdrehen

        kaempfer_links.zeichnen(bildschirm)
        kaempfer_rechts.zeichnen(bildschirm)

        if not runde_beendet:
            if not kaempfer_links.alive or not kaempfer_rechts.alive or round_time == 0:
                runde_beendet = True
                pause_start = pygame.time.get_ticks()
                if kaempfer_links.gesundheit > kaempfer_rechts.gesundheit:
                    siege_links += 1
                else:
                    siege_rechts += 1

        if runde_beendet:
            ko = big_font.render("K.O.", True, weiß)
            bildschirm.blit(ko, (bildschirmbreite // 2 - 60, 120))

            if pygame.time.get_ticks() - pause_start > 2000:
                if siege_links == 2 or siege_rechts == 2:
                    modus = "auswahl"
                    siege_links = 0
                    siege_rechts = 0
                    runde = 1
                    
                else:
                    runde += 1
                    runde_beendet = False
                    kaempfer_links.gesundheit = 100
                    kaempfer_rechts.gesundheit = 100
                    kaempfer_links.alive = True
                    kaempfer_rechts.alive = True
                    kaempfer_links.rechteck.x = 300
                    kaempfer_rechts.rechteck.x = 700
                    kaempfer_links.rechteck.y = spawn_y
                    kaempfer_rechts.rechteck.y = spawn_y
                    round_start = pygame.time.get_ticks()

    pygame.display.update()

pygame.quit()
