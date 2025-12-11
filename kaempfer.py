import pygame

import pygame


class Kaempfer:
    def __init__(self, x, y, spieler_nummer, gegner=None, sprite_datei=None, animation_schritte=None, frame_size=64, animation_data=None):
        
        # Setze Sprite-Größe (Default 64, kann übergeben werden)
        self.größe = frame_size
        
        # Animation-Daten: [(sheet, frame_w, frame_h, frame_count), ...]
        # Index: 0=IDLE, 1=RUN, 2=ATTACK, 3=HURT
        self.animation_data = animation_data
        self.current_animation = 0  # 0=IDLE
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 5  # Frames zwischen Animation-Frames (höher = langsamer)

        self.umdrehen = False

        self.animation_liste = self.lade_sprites(sprite_datei, animation_schritte) if sprite_datei and animation_schritte else None

        self.aktion = 0  # 0 = IDLE

        self.frame_index = 0 

        # Setze das initiale Bild nur, wenn Animationen geladen wurden
        if self.animation_liste is not None:
            self.image = self.animation_liste[self.aktion][self.frame_index]
        else:
            # Erstelle ein leeres Placeholder-Bild, falls keine Sprites geladen wurden
            self.image = pygame.Surface((self.größe, self.größe))
            self.image.fill((200, 200, 200))

        # Rechteck als Platzhalter für die Spielfigur
        self.rechteck = pygame.Rect(x, y, 150, 300)

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
        self.angriff_schaden_verursacht = False  # Flag um doppelten Schaden zu verhindern

        #Gesundheit des Kämpfers
        self.gesundheit = 100

        # Gegner-Referenz (wird später gesetzt)
        self.gegner = gegner #speichert den Gegner des Kämpfers

    
    #Laden von Sprites
    def lade_sprites(self, sprite_datei, animation_schritte):
        print(f"Sprite-Datei Größe: {sprite_datei.get_width()}x{sprite_datei.get_height()}")
        print(f"Frame-Größe: {self.größe}x{self.größe}")
        print(f"Animation-Schritte: {animation_schritte}")
        
        animation_liste = []
        for y, frames_count in enumerate(animation_schritte):
            temp_img_list = []        
            for x in range(frames_count):  # Iteriere über die Anzahl der Frames für diese Animation
                try:
                    temp_img = sprite_datei.subsurface(x * self.größe, y * self.größe, self.größe, self.größe) 
                    temp_img_list.append(temp_img)
                    if x == 0:
                        print(f"Animation {y}, Frame 0 extrahiert: ({x * self.größe}, {y * self.größe}) -> {self.größe}x{self.größe}")
                except ValueError as e:
                    print(f"FEHLER bei Animation {y}, Frame {x}: {e}")
            animation_liste.append(temp_img_list)
        print(f"Animationen geladen: {len(animation_liste)} Animationen, erste mit {len(animation_liste[0]) if animation_liste else 0} Frames")    
        return animation_liste    

            
    # Bewegung des Kämpfers
    
    def bewegen(self, bildschirmbreite, bildschirmhoehe, oberflaeche, gegner):
        GESCHWINDIGKEIT = 10
        SCHWERKRAFT = 2
        dx = 0
        dy = 0

        # Tasten erfassen
        tasten = pygame.key.get_pressed()

        # Bestimme die aktuelle Animation basierend auf Spieleraktion
        ist_bewegung = False
        
        # links/rechts bewegen (Spieler 1: A/D, Spieler 2: Pfeiltasten)
        if self.spieler_nummer == 1:
            if tasten[pygame.K_a]:
                dx = -GESCHWINDIGKEIT
                ist_bewegung = True
            if tasten[pygame.K_d]:
                dx = GESCHWINDIGKEIT
                ist_bewegung = True
        else:  # Spieler 2
            if tasten[pygame.K_LEFT]:
                dx = -GESCHWINDIGKEIT
                ist_bewegung = True
            if tasten[pygame.K_RIGHT]:
                dx = GESCHWINDIGKEIT
                ist_bewegung = True
        
        # Setze Animation basierend auf Zustand
        if self.angriff_aktiv:
            self.current_animation = 2  # ATTACK
        elif ist_bewegung:
            self.current_animation = 1  # RUN
        else:
            self.current_animation = 0  # IDLE
        
        # Update frame animation
        if self.animation_data is not None:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                sheet, frame_w, frame_h, frame_count = self.animation_data[self.current_animation]
                self.frame_index = (self.frame_index + 1) % frame_count
                # Extrahiere den aktuellen Frame
                try:
                    self.image = sheet.subsurface(self.frame_index * frame_w, 0, frame_w, frame_h)
                except:
                    pass

        # springen (Spieler 1: W, Spieler 2: UP), nur wenn nicht schon gesprungen wird
        jump_taste = tasten[pygame.K_w] if self.spieler_nummer == 1 else tasten[pygame.K_UP]
        if jump_taste and not self.springen:
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

        #Sicherstellen Kämpfer einander gegenüberstehen 
        if gegner.rechteck.centerx > self.rechteck.centerx:
            self.umdrehen = False
        else:
            self.umdrehen = True

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
            # Übergebe den Gegner, damit Kollisionen geprüft und Schaden verursacht wird
            ziel = getattr(self, 'gegner', None)
            self.angriff(oberflaeche, ziel)

            # Angriff beenden, wenn Dauer vorbei
            if jetzt >= self.angriff_ende_zeit:
                self.angriff_aktiv = False
                # Cooldown-Zeit setzen
                self.angriff_schaden_verursacht = False  # Flag zurücksetzen
                self.angriff_ende_zeit = jetzt + ANGRIFF_COOLDOWN

    
    # Angriff
    
    def angriff(self, oberflaeche, gegner=None):
        # Angriff abhängig von umdrehen-Flag (wer schaut nach links/rechts)
        if self.umdrehen:
            # Kämpfer schaut nach links, schlägt nach links
            start_x = self.rechteck.centerx - 2 * self.rechteck.width
        else:
            # Kämpfer schaut nach rechts, schlägt nach rechts
            start_x = self.rechteck.centerx

        attacke_rechteck = pygame.Rect(
            start_x,
            self.rechteck.y,
            2 * self.rechteck.width,
            self.rechteck.height,
        )

        # Prüfe Kollision mit dem Gegner, falls einer übergeben wurde
        ziel = gegner if gegner is not None else getattr(self, 'gegner', None)
        if ziel is not None and attacke_rechteck.colliderect(ziel.rechteck):
            # Verursache Schaden nur einmal pro Angriff
            if not self.angriff_schaden_verursacht:
                ziel.gesundheit -= 10  # Treffer: Gegner verliert 10 Gesundheit
                self.angriff_schaden_verursacht = True

        pygame.draw.rect(oberflaeche, (0, 255, 0), attacke_rechteck)

    
    # Zeichnen des Kämpfers
    
    def zeichnen(self, oberflaeche):
        # Zeichne das Sprite-Bild nur, wenn Animationen geladen wurden
        if self.animation_liste is not None:
            # Skaliere das Bild auf die Größe des Rechtecks (80x180)
            scaled_image = pygame.transform.scale(self.image, (self.rechteck.width, self.rechteck.height))
            # Spiegle das Bild, wenn der Kämpfer nach links schaut
            if self.umdrehen:
                scaled_image = pygame.transform.flip(scaled_image, True, False)
            oberflaeche.blit(scaled_image, (self.rechteck.x, self.rechteck.y))
        else:
            # Zeige nur den roten Platzhalter, wenn keine Sprite geladen wurde
            pygame.draw.rect(oberflaeche, (255, 0, 0), self.rechteck)