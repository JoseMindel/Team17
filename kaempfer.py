import pygame

import pygame


class Kaempfer:
    def __init__(self, x, y, spieler_nummer):
        # Rechteck als Platzhalter für die Spielfigur
        self.rechteck = pygame.Rect(x, y, 80, 180)

        # Vertikale Geschwindigkeit (für Sprung/Schwerkraft)
        self.geschwindigkeit_y = 0

        # Merker, ob der Kämpfer gerade in der Luft ist
        self.springen = False

        # (noch nicht genutzt, könnte für verschiedene Attacken dienen)
        self.angriffstyp = 0

        # 1 = Spieler 1, 2 = Spieler 2
        self.spieler_nummer = spieler_nummer

        # Angriffszustand (für Dauer + Cooldown)
        self.angriff_aktiv = False
        self.angriff_ende_zeit = 0

    
    # Bewegung des Kämpfers
    
    def bewegen(self, bildschirmbreite, bildschirmhoehe, oberflaeche):
        GESCHWINDIGKEIT = 10
        SCHWERKRAFT = 2
        dx = 0
        dy = 0

        # Tasten erfassen
        tasten = pygame.key.get_pressed()

        # links/rechts bewegen (A und D)
        if tasten[pygame.K_a]:
            dx = -GESCHWINDIGKEIT
        if tasten[pygame.K_d]:
            dx = GESCHWINDIGKEIT

        # springen (W), nur wenn nicht schon gesprungen wird
        if tasten[pygame.K_w] and not self.springen:
            self.geschwindigkeit_y = -30
            self.springen = True

        # Schwerkraft hinzufügen
        self.geschwindigkeit_y += SCHWERKRAFT
        dy += self.geschwindigkeit_y

        # Bildschirmgrenzen links/rechts
        if self.rechteck.left + dx < 0:
            dx = -self.rechteck.left
        if self.rechteck.right + dx > bildschirmbreite:
            dx = bildschirmbreite - self.rechteck.right

        # Boden-Kollision (ein bisschen Abstand zum unteren Rand)
        boden_hoehe = bildschirmhoehe - 110
        if self.rechteck.bottom + dy > boden_hoehe:
            dy = boden_hoehe - self.rechteck.bottom
            self.geschwindigkeit_y = 0
            self.springen = False

        # Position aktualisieren
        self.rechteck.x += dx
        self.rechteck.y += dy

        # ===== Angriff / Cooldown-Logik =====
        jetzt = pygame.time.get_ticks()
        ANGRIFF_DAUER = 200      # wie lange der Angriff sichtbar ist (ms)
        ANGRIFF_COOLDOWN = 400   # Wartezeit bis zum nächsten Angriff (ms)

        # Angriff starten, wenn richtige Taste gedrückt wird
        # und gerade kein Angriff aktiv ist und Cooldown vorbei ist
        taste_gedrueckt_spieler1 = self.spieler_nummer == 1 and tasten[pygame.K_r]
        taste_gedrueckt_spieler2 = self.spieler_nummer == 2 and tasten[pygame.K_t]

        if (taste_gedrueckt_spieler1 or taste_gedrueckt_spieler2) \
                and not self.angriff_aktiv \
                and jetzt >= self.angriff_ende_zeit:
            self.angriff_aktiv = True
            self.angriff_ende_zeit = jetzt + ANGRIFF_DAUER

        # Solange der Angriff aktiv ist, Hitbox zeichnen
        if self.angriff_aktiv:
            self.angriff(oberflaeche)

            # Angriff beenden, wenn Dauer vorbei
            if jetzt >= self.angriff_ende_zeit:
                self.angriff_aktiv = False
                # Cooldown-Zeit setzen
                self.angriff_ende_zeit = jetzt + ANGRIFF_COOLDOWN

    
    # Angriff
    
    def angriff(self, oberflaeche):
        # Angriffshitze abhängig von der Spielerseite
        if self.spieler_nummer == 1:
            # Spieler 1 schlägt nach rechts
            start_x = self.rechteck.centerx
        else:
            # Spieler 2 schlägt nach links
            start_x = self.rechteck.centerx - 2 * self.rechteck.width

        attacke_rechteck = pygame.Rect(
            start_x,
            self.rechteck.y,
            2 * self.rechteck.width,
            self.rechteck.height,
        )

        # Wenn du später Kollision machen willst, kannst du hier
        # gegen den Gegner prüfen.
        # Beispiel (Pseudocode):
        # if attacke_rechteck.colliderect(gegner.rechteck):
        #     print("Treffer!")

        pygame.draw.rect(oberflaeche, (0, 255, 0), attacke_rechteck)

    
    # Zeichnen des Kämpfers
    
    def zeichnen(self, oberflaeche):
        pygame.draw.rect(oberflaeche, (255, 0, 0), self.rechteck)