import pygame


class Kaempfer:
    """Kurze, klare Kämpferklasse – nur Animation & Bewegung, kein Sound."""
    
    def __init__(self, x, y, spieler_nummer, daten, sprite_sheet, animation_schritte, gegner=None):
        # daten: [size, scale, offset]
        self.size = daten[0]
        self.image_scale = daten[1]
        self.offset = daten[2]

        self.spieler_nummer = spieler_nummer
        self.gegner = gegner

        # Collision-Rechteck (logische Position). x/y sind oben-links.
        # Das Sprite wird über offset/scale relativ zum Rechteck gezeichnet.
        self.box_width = 100
        self.box_height = 220
        self.rechteck = pygame.Rect(x, y, self.box_width, self.box_height)

        # Animations-Schritte/Sheet merken und laden
        self.animation_steps = animation_schritte
        self.sprite_sheet = sprite_sheet
        self.animations_liste = self.lade_sprites(self.sprite_sheet, self.animation_steps)
        self.frame_index = 0
        # Aktionen: 0=idle, 1=run, 2=jump, 3=attack, 4=hurt, 5=death
        self.aktion = 0
        self.bild = self.animations_liste[self.aktion][self.frame_index] if self.animations_liste else None
        self.update_time = pygame.time.get_ticks()

        # Zustand
        self.running = False
        self.springen = False
        self.geschwindigkeit_y = 0
        self.angriff_aktiv = False
        self.angriff_schaden_verursacht = False
        self.hurt = False
        self.gesundheit = 100
        self.alive = True
        self.umdrehen = False
        
        # Angriffsstärke und Hitbox
        self.angriff_schaden = 10
        self.angriff_hitbox_ratio = (0.5, 0.4, 0.3)  # (width_ratio, height_ratio, y_offset_ratio)
        
        # Cooldown
        self.angriff_ende_zeit = 0
        self.hurt_dauer = 300
        self.hurt_ende_zeit = 0
        
        # Frame-Timing
        self.frame_verzoegerung = 5
        self.frame_zeitgeber = 0

    def lade_sprites(self, sprite_sheet=None, animation_steps=None):
        """Laden und Slicing von Sprite-Frames."""
        # Fallback auf im Objekt gespeicherte Werte
        sprite_sheet = sprite_sheet or self.sprite_sheet
        animation_steps = animation_steps or self.animation_steps
        
        if sprite_sheet is None or animation_steps is None:
            return []
        
        animations_liste = []
        for y_zeile, frames_anzahl in enumerate(animation_steps):
            temp_img_list = []
            for x_frame in range(frames_anzahl):
                try:
                    x = x_frame * self.size
                    y = y_zeile * self.size
                    frame = sprite_sheet.subsurface((x, y, self.size, self.size))
                    s = pygame.transform.scale(frame, (self.size * self.image_scale, self.size * self.image_scale))
                    temp_img_list.append(s)
                except Exception:
                    # Fallback: leere Oberfläche
                    s = pygame.Surface((self.size * self.image_scale, self.size * self.image_scale), pygame.SRCALPHA)
                    temp_img_list.append(s)
            animations_liste.append(temp_img_list)
        
        return animations_liste

    def move(self, bildschirmbreite, bildschirmhoehe, oberflaeche, gegner):
        """Bewegung für Spieler 1 (A/D/W, R für Angriff)."""
        GESCHWINDIGKEIT = 10
        SCHWERKRAFT = 2
        dx = 0
        dy = 0

        # wenn tot = nur noch death animation, keine steuerung mehr
        if not self.alive:
            self.aktion = 6   # death
            self._aktualisiere_frame()
            return

        tasten = pygame.key.get_pressed()
        self.running = False

        # Behandle Hurt (Stun)
        jetzt = pygame.time.get_ticks()
        if jetzt < self.hurt_ende_zeit:
            self._aktualisiere_frame()
            self.geschwindigkeit_y += SCHWERKRAFT
            dy += self.geschwindigkeit_y
            boden = bildschirmhoehe - 110
            if self.rechteck.bottom + dy > boden:
                dy = boden - self.rechteck.bottom
                self.geschwindigkeit_y = 0
                self.springen = False
            self.rechteck.y += dy
            return

        # Bewegung
        if tasten[pygame.K_a]:
            dx = -GESCHWINDIGKEIT
            self.running = True
        if tasten[pygame.K_d]:
            dx = GESCHWINDIGKEIT
            self.running = True

        # Springen
        if tasten[pygame.K_w] and not self.springen:
            self.geschwindigkeit_y = -30
            self.springen = True

        # Angriff
        if tasten[pygame.K_r] and not self.angriff_aktiv and jetzt >= self.angriff_ende_zeit:
            self.angriff_aktiv = True
            self.angriff_ende_zeit = jetzt + 200

        # Setze Aktion
        if self.angriff_aktiv:
            self.aktion = 3  # ATTACK
        elif self.springen:
            self.aktion = 2  # JUMP
        elif self.running:
            self.aktion = 1  # RUN
        else:
            self.aktion = 0  # IDLE

        # Animation aktualisieren
        self._aktualisiere_frame()

        # Schwerkraft
        self.geschwindigkeit_y += SCHWERKRAFT
        dy += self.geschwindigkeit_y

        # Bildschirmgrenzen: Sprite muss vollständig auf dem Bildschirm bleiben
        if self.rechteck.left + dx < 0:
            dx = -self.rechteck.left
        elif self.rechteck.right + dx > bildschirmbreite:
            dx = bildschirmbreite - self.rechteck.right

        # Boden-Kollision
        boden = bildschirmhoehe - 110
        if self.rechteck.bottom + dy > boden:
            dy = boden - self.rechteck.bottom
            self.geschwindigkeit_y = 0
            self.springen = False

        # Blickrichtung gegenüber Gegner
        if gegner and hasattr(gegner, 'rechteck'):
            if gegner.rechteck.centerx > self.rechteck.centerx:
                self.umdrehen = False
            else:
                self.umdrehen = True

        # Position aktualisieren
        self.rechteck.x += dx
        self.rechteck.y += dy

        # Angriff-Logik
        if self.angriff_aktiv:
            self._angriff(oberflaeche, gegner)
            if pygame.time.get_ticks() >= self.angriff_ende_zeit:
                self.angriff_aktiv = False
                self.angriff_schaden_verursacht = False
                self.angriff_ende_zeit = pygame.time.get_ticks() + 400

    def move2(self, bildschirmbreite, bildschirmhoehe, oberflaeche, gegner):
        """Bewegung für Spieler 2 (Pfeiltasten, T für Angriff)."""
        GESCHWINDIGKEIT = 10
        SCHWERKRAFT = 2
        dx = 0
        dy = 0

        # wenn tot = nur noch death animation, keine steuerung mehr
        if not self.alive:
            self.aktion = 6   # death
            self._aktualisiere_frame()
            return

        tasten = pygame.key.get_pressed()
        self.running = False

        # Behandle Hurt (Stun)
        jetzt = pygame.time.get_ticks()
        if jetzt < self.hurt_ende_zeit:
            self._aktualisiere_frame()
            self.geschwindigkeit_y += SCHWERKRAFT
            dy += self.geschwindigkeit_y
            boden = bildschirmhoehe - 110
            if self.rechteck.bottom + dy > boden:
                dy = boden - self.rechteck.bottom
                self.geschwindigkeit_y = 0
                self.springen = False
            self.rechteck.y += dy
            return

        # Bewegung
        if tasten[pygame.K_LEFT]:
            dx = -GESCHWINDIGKEIT
            self.running = True
        if tasten[pygame.K_RIGHT]:
            dx = GESCHWINDIGKEIT
            self.running = True

        # Springen
        if tasten[pygame.K_UP] and not self.springen:
            self.geschwindigkeit_y = -30
            self.springen = True

        # Angriff
        if tasten[pygame.K_t] and not self.angriff_aktiv and jetzt >= self.angriff_ende_zeit:
            self.angriff_aktiv = True
            self.angriff_ende_zeit = jetzt + 200

        # Setze Aktion
        if self.angriff_aktiv:
            self.aktion = 3  # ATTACK
        elif self.springen:
            self.aktion = 2  # JUMP
        elif self.running:
            self.aktion = 1  # RUN
        else:
            self.aktion = 0  # IDLE

        # Animation aktualisieren
        self._aktualisiere_frame()

        # Schwerkraft
        self.geschwindigkeit_y += SCHWERKRAFT
        dy += self.geschwindigkeit_y

        # Bildschirmgrenzen: Sprite muss vollständig auf dem Bildschirm bleiben
        if self.rechteck.left + dx < 0:
            dx = -self.rechteck.left
        elif self.rechteck.right + dx > bildschirmbreite:
            dx = bildschirmbreite - self.rechteck.right

        # Boden-Kollision
        boden = bildschirmhoehe - 110
        if self.rechteck.bottom + dy > boden:
            dy = boden - self.rechteck.bottom
            self.geschwindigkeit_y = 0
            self.springen = False

        # Blickrichtung gegenüber Gegner
        if gegner and hasattr(gegner, 'rechteck'):
            if gegner.rechteck.centerx > self.rechteck.centerx:
                self.umdrehen = False
            else:
                self.umdrehen = True

        # Position aktualisieren
        self.rechteck.x += dx
        self.rechteck.y += dy

        # Angriff-Logik
        if self.angriff_aktiv:
            self._angriff(oberflaeche, gegner)
            if pygame.time.get_ticks() >= self.angriff_ende_zeit:
                self.angriff_aktiv = False
                self.angriff_schaden_verursacht = False
                self.angriff_ende_zeit = pygame.time.get_ticks() + 400

    def _aktualisiere_frame(self):
        """Frame-Animation aktualisieren."""
        if self.gesundheit <= 0 and self.alive:
            self.gesundheit = 0
            self.alive = False
            self.aktion = 6  # Tod
            self.frame_index = 0

        if not self.animations_liste:
            return
        
        self.frame_zeitgeber += 1
        if self.frame_zeitgeber >= self.frame_verzoegerung:
            self.frame_zeitgeber = 0
            frames = self.animations_liste[self.aktion]

            #todes animation: nur bis zum letzten bild, kein loop
            if self.aktion == 6:   # Tod
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
            else:
                self.frame_index = (self.frame_index + 1) % len(frames)

            self.bild = frames[self.frame_index]

    def _angriff(self, oberflaeche, gegner):
        """Angriff ausführen und Schaden austeilen."""
        w = int(self.rechteck.width * self.angriff_hitbox_ratio[0])
        h = int(self.rechteck.height * self.angriff_hitbox_ratio[1])
        y_off = int(self.rechteck.height * self.angriff_hitbox_ratio[2])
        
        if self.umdrehen:
            start_x = self.rechteck.left - w
        else:
            start_x = self.rechteck.right
        
        hitbox = pygame.Rect(start_x, self.rechteck.y + y_off, w, h)
        
        # Collision
        if gegner and hitbox.colliderect(gegner.rechteck):
            if not self.angriff_schaden_verursacht:
                gegner.take_damage(self.angriff_schaden)
                self.angriff_schaden_verursacht = True
        
        # Debug hitbox
        # pygame.draw.rect(oberflaeche, (0, 255, 0), hitbox)

    def take_damage(self, amount):
        """Schaden erleiden."""
        self.gesundheit = max(0, self.gesundheit - amount)
        self.hurt = True
        self.hurt_ende_zeit = pygame.time.get_ticks() + self.hurt_dauer

    def zeichnen(self, oberflaeche):
        """Kämpfer zeichnen."""
        if self.bild is not None:
            img = self.bild
            if self.umdrehen:
                img = pygame.transform.flip(img, True, False)
            # Wie im Referenzcode: Sprite relativ zum Collision-Rechteck zeichnen
            draw_x = self.rechteck.x - (self.offset[0] * self.image_scale)
            draw_y = self.rechteck.y - (self.offset[1] * self.image_scale)
            oberflaeche.blit(img, (draw_x, draw_y))
