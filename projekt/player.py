import os
import pygame
from projekt.config import *
import time

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, platforms, borders, ladders, ladders_detect):
        super().__init__()

        self.x = x
        self.y = y
        self.height = PLAYER_HEIGHT
        self.width = PLAYER_WIDTH
        self.speed = PLAYER_SPEED
        self.jump = PLAYER_JUMP

        self.vel_y = PLAYER_VER_VELOCITY
        self.vel_x = PLAYER_HOR_VELOCITY
        self.gravity = GRAVITY

        self.platforms = platforms
        self.borders = borders
        self.ladders = ladders

        self.ladder_detects = ladders_detect

        self.ladder_mode = False
        self.detect_mode = False
        self.detect_entry_y = 0

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        #najveca visina potrebno za treniranje neat
        self.best_y = self.rect.y

        #potrebno da ne dopusti da igrac postane superman
        #self.can_jump = False

        #potrebno za novu update_neat_players metodu
        self.hit_barrel = False

        self.last_jump_time = 0  # vrijeme zadnjeg skoka
        self.jump_cooldown = 1.0  # cooldown u sekundama

        self.jumping = False
        self.y_at_jump = None

        self.animations = {
            'down': [
                self.load_scaled_image('mario_up_1.png', self.width, self.height),
                self.load_scaled_image('mario_up_2.png', self.width, self.height)
            ],
            'up': [
                self.load_scaled_image('mario_up_1.png', self.width, self.height),
                self.load_scaled_image('mario_up_2.png', self.width, self.height)
            ],
            'left': [
                self.load_scaled_image('mario_run_left1.png', self.width, self.height),
                self.load_scaled_image('mario_run_left2.png', self.width, self.height)
            ],
            'right': [
                self.load_scaled_image('mario_run_right1.png', self.width, self.height),
                self.load_scaled_image('mario_run_right2.png', self.width, self.height)
            ],
        }

        self.idle_images = {
            'left': self.load_scaled_image('mario_left.png', self.width, self.height),
            'right': self.load_scaled_image('mario_right.png', self.width, self.height),
        }

        self.moving = False
        self.direction = 'right'
        self.image_index = 0
        self.animation_counter = 0
        self.image = self.animations[self.direction][self.image_index]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update_animation(self):
        if self.on_ladder() and abs(self.vel_y) > 0:
            ladder_dir = 'up' if self.vel_y < 0 else 'down'
            seq = self.animations[ladder_dir]
            self.animation_counter += 1
            if self.animation_counter >= 5:
                self.animation_counter = 0
                self.image_index = (self.image_index + 1) % len(seq)
            self.image = seq[self.image_index]

        elif self.moving:
            seq = self.animations[self.direction]
            self.animation_counter += 1
            if self.animation_counter >= 5:
                self.animation_counter = 0
                self.image_index = (self.image_index + 1) % len(seq)
            self.image = seq[self.image_index]

        else:
            self.image_index = 0
            self.animation_counter = 0
            self.image = self.idle_images[self.direction]

    def load_scaled_image(self, filename, width, height):
        path = os.path.join('projekt', 'Assets', filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (width, height))


    def move_left(self):
        self.x -= self.speed
        #self.vel_y += self.gravity
        #self.y += self.vel_y

        self.rect.x = self.x
        #self.rect.y = self.y
        self.direction = 'left'
        self.moving = True

    def move_right(self):
        self.x += self.speed
        #self.vel_y += self.gravity
        #self.y += self.vel_y

        self.rect.x = self.x
        #self.rect.y = self.y
        self.direction = 'right'
        self.moving = True

    def move_up(self):
        self.y -= self.speed
        self.vel_y += self.gravity
        self.y += self.vel_y

        self.rect.x = self.x
        self.rect.y = self.y
        self.direction = 'up'
        self.moving = True

    def move_down(self):
        self.y += self.speed
        self.vel_y += self.gravity
        self.y += self.vel_y

        self.rect.x = self.x
        self.rect.y = self.y
        self.direction = 'down'
        self.moving = True

    def upup(self):
        self.vel_y = -self.jump
        self.direction = 'up'
        self.moving = True

    def move(self, keys):
        prev_y = self.y
        prev_x = self.x

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_left()
            self.direction = 'left'
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_right()
            self.direction = 'right'
            self.moving = True

        current_time = time.time()
        if keys[pygame.K_SPACE] and self.is_grounded():
            if current_time - self.last_jump_time >= self.jump_cooldown:
                self.upup()
                self.last_jump_time = current_time

        return prev_y, prev_x

    def is_grounded(self):
        '''for platform in self.platforms:
            if (abs(self.rect.bottom - platform.rect.top) <= 10 and
                self.rect.right > platform.rect.left and
                self.rect.left < platform.rect.right):
                return True
        return False'''
        for platform in self.platforms:
            if (abs(self.rect.bottom - platform.rect.top) <= 10 and
                    self.rect.right > platform.rect.left and
                    self.rect.left < platform.rect.right and
                    self.rect.centery < platform.rect.top):  #igrac mora biti iznad platforme
                return True
        return False

    def check_collision_border(self, borders, prev_x):
        '''for border in borders:
            if self.rect.colliderect(border.rect):
                if border.rect.width < border.rect.height:
                    if prev_x + self.width <= border.rect.left:
                        self.x = border.rect.left - self.width
                    elif prev_x >= border.rect.right:
                        self.x = border.rect.right
                    self.rect.x = self.x'''
        for border in borders:
            if self.rect.colliderect(border.rect):
                #odbijanje od vertikalnog bordera
                if border.rect.width < border.rect.height:
                    if prev_x + self.width <= border.rect.left:
                        self.x = border.rect.left - self.width  #odbijanje s lijeve strane
                    elif prev_x >= border.rect.right:
                        self.x = border.rect.right  #odbijanje s desne strane
                #odbijanje od poda ili stropa
                #vjv nece nikad trebat al za svaki slucaj
                else:
                    if self.vel_y > 0 and self.rect.bottom > border.rect.top:
                        self.y = border.rect.top - self.height  #odbijanje odozdo
                        self.vel_y = 0
                    elif self.vel_y < 0 and self.rect.top < border.rect.bottom:
                        self.y = border.rect.bottom  #odbojanje odozgo
                        self.vel_y = 0

                self.rect.x = self.x
                self.rect.y = self.y

    def vertically_collide(self, platforms, prev_y):
        self.rect.y = self.y
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # ako udari u platformu u skoku odbija ga
                if prev_y >= platform.rect.bottom and self.vel_y < 0:
                    self.y = platform.rect.bottom + 1
                    self.vel_y = 0
                    self.rect.y = self.y
                    #print("1 udario glavom i odbijen")
                    #print("-------------------")
                    # self.can_jump = False  # AKO PUKNE I OVO JE RAZLOG
                # snapanje igraca na platformu ako pada
                elif (prev_y + self.height <= platform.rect.top and
                      self.rect.bottom >= platform.rect.top and
                      self.vel_y >= 0):
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.rect.y = self.y
                    #print("pao na platformu")
                    # self.can_jump = True  # AKO PUKNE OVO JE RAZLOG

    def horizontal_steps(self, platforms, prev_x):
        step_height = 15
        self.rect.x = self.x

        if self.is_grounded():
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if prev_x + self.width <= platform.rect.left:
                        can_step = False
                        for step in range(1, step_height + 1):
                            self.rect.y = self.y - step
                            if not self.rect.colliderect(platform.rect):
                                can_step = True
                                self.y -= step
                                #print("2 penje se desno")
                                break
                        if not can_step:
                            self.x = platform.rect.left - self.width
                        self.rect.x = self.x
                        self.rect.y = self.y

                    elif prev_x >= platform.rect.right:
                        can_step = False
                        for step in range(1, step_height + 1):
                            self.rect.y = self.y - step
                            if not self.rect.colliderect(platform.rect):
                                can_step = True
                                self.y -= step
                                #print("2 penje se lijevo")
                                break
                        if not can_step:
                            self.x = platform.rect.right
                        self.rect.x = self.x
                        self.rect.y = self.y

    def check_collision_platform(self, platforms, prev_y, prev_x):
        self.vertically_collide(platforms, prev_y)
        self.horizontal_steps(platforms, prev_x)

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                #print("Kolizija detektirana:")
                #print(f"IGRAČ: {self.rect}, PLATFORM: {platform.rect}")
                #print(f"Prethodne pozicije -> prev_x={prev_x}, prev_y={prev_y}")
                #print(f"Trenutne pozicije -> x={self.x}, y={self.y}, vel_y={self.vel_y}")

                # Provjeri dolazi li igrač odozgo i postavi ga na platformu
                if prev_y + self.height <= platform.rect.top:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    #print("Igrač postavljen na platformu (odozgo).")

                # Ako igrač udara platformu odozdo, odbaci ga prema dolje
                elif prev_y >= platform.rect.bottom:
                    self.y = platform.rect.bottom
                    self.vel_y = 0
                    #print("Igrač izbačen ISPOD platforme (udar odozdo).")

                # Bočna kolizija (lijevo ili desno)
                else:
                    if prev_x + self.width <= platform.rect.left:
                        self.x = platform.rect.left - self.width
                        #print("Odbijanje od LIJEVOG ruba platforme.")
                    elif prev_x >= platform.rect.right:
                        self.x = platform.rect.right
                        #print("Odbijanje od DESNOG ruba platforme.")
                    else:
                        # Ako je baš zaglavio, prisilno ga izbaci dolje
                        self.y = platform.rect.bottom
                        self.vel_y = 0
                        #print("Hitna korekcija - igrač izbačen ISPOD platforme (prisilno).")

                # Provjera odbijanja od lijevog ili desnog bordera
                if prev_x + self.width <= platform.rect.left:
                    self.x = platform.rect.left - self.width
                    #print("Odbijanje od LIJEVOG bordera.")
                elif prev_x >= platform.rect.right:
                    self.x = platform.rect.right
                    #print("Odbijanje od DESNOG bordera.")

                # ažuriranje rect pozicija igrača nakon odbijanja
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)

    def on_ladder_detect(self):
        for ld in self.ladder_detects:
            if self.rect.colliderect(ld.rect):
                return True
        return False

    def on_ladder(self):
        for ladder in self.ladders:
            if self.rect.colliderect(ladder.rect):
                return True
        return False

    def climb_ladder(self, keys):
        '''if keys[pygame.K_w]:
            self.y -= self.speed
            self.vel_y = 0
        elif keys[pygame.K_s]:
            self.y += self.speed
            self.vel_y = 0'''
        '''if self.is_grounded():
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.move_right()
        self.rect.x = self.x
        self.rect.y = self.y'''
        pass

    def update_player(self, keys, platforms):
        '''prev_y, prev_x = self.y, self.x
        #print("grounded:", self.is_grounded(), "VelY:", self.vel_y)

        if self.on_ladder():
            self.climb_ladder(keys)
        else:
            prev_y, prev_x = self.move(keys)

            # SKOK (provjera)
            current_time = time.time()
            if keys[pygame.K_SPACE] and self.is_grounded():
                if current_time - self.last_jump_time >= self.jump_cooldown:
                    self.upup()
                    self.last_jump_time = current_time

            # gravitacija
            self.vel_y += self.gravity
            self.y += self.vel_y
            self.rect.y = self.y

        # provjera kolizija
        self.check_collision_platform(platforms, prev_y, prev_x)
        self.check_collision_border(self.borders, prev_x)'''
        # Enter detect-only mode: when on detect zone, not on ladder, pressing down/up
        self.moving = False
        if not self.ladder_mode and not self.detect_mode:
            if self.on_ladder_detect() and not self.on_ladder() and (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                self.detect_mode = True
                self.detect_entry_y = self.y
                self.vel_y = 0

        # Handle detect-only descending/ascending
        if self.detect_mode:
            # Exit on horizontal input
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]:
                self.detect_mode = False
                return
            # Move down
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y += self.speed
            # Move up, but not above entry point
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y -= self.speed
                if self.y < self.detect_entry_y:
                    self.y = self.detect_entry_y
            self.rect.y = int(self.y)
            # If reaches ladder, exit detect mode
            if self.on_ladder():
                self.detect_mode = False
                # now ladder_mode can activate next frame if input
                return
            return

        # Attempt to enter ladder mode when on detect + ladder and pressing vertical
        if not self.ladder_mode:
            if self.on_ladder_detect() and self.on_ladder() and (
                    keys[pygame.K_UP] or keys[pygame.K_w] or
                    keys[pygame.K_DOWN] or keys[pygame.K_s]):
                self.ladder_mode = True
                self.vel_y = 0

        # Ladder mode: only vertical movement, no gravity
        if self.ladder_mode:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y -= self.speed
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y += self.speed
            self.rect.y = int(self.y)

            # Exit if off ladder
            if not self.on_ladder():
                self.ladder_mode = False
                return

            # Landing on a platform when descending from ladder
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                for platform in platforms:
                    if self.rect.colliderect(platform.rect) and self.rect.bottom > platform.rect.top:
                        self.y = platform.rect.top - self.height
                        self.rect.y = int(self.y)
                        self.ladder_mode = False
                        return
            return

        # Standard movement when not in ladder or detect mode
        prev_y, prev_x = self.y, self.x
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_right()

        current_time = time.time()
        if keys[pygame.K_SPACE] and self.is_grounded():
            if current_time - self.last_jump_time >= self.jump_cooldown:
                self.upup()
                self.last_jump_time = current_time

        self.vel_y += self.gravity
        self.y += self.vel_y

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.check_collision_platform(platforms, prev_y, prev_x)
        self.check_collision_border(self.borders, prev_x)

        self.update_animation()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def get_network_inputs(self, ladders, barrels, princess_y):
        norm_x = self.rect.x / SCREEN_WIDTH
        norm_y = self.rect.y / SCREEN_HEIGHT
        grounded = 1.0 if self.is_grounded() else 0.0
        on_ladder = 1.0 if self.on_ladder() else 0.0
        climbing = 0.0
        distance_to_princess_y = (princess_y - self.rect.y) / SCREEN_HEIGHT
        if ladders:
            nearest_ladder = min(ladders, key=lambda l: abs(l.rect.x - self.rect.x))
            ladder_x = nearest_ladder.rect.x / SCREEN_WIDTH
        else:
            ladder_x = 0.0
        if barrels:
            nearest_barrel = min(barrels, key=lambda b: abs(b.rect.x - self.rect.x))
            barrel_x = nearest_barrel.rect.x / SCREEN_WIDTH
            barrel_y = nearest_barrel.rect.y / SCREEN_HEIGHT
            barrel_vel_x = nearest_barrel.vel_x / BARREL_SPEED if hasattr(nearest_barrel, 'vel_x') else 0.0
            barrel_vel_y = nearest_barrel.vel_y / BARREL_SPEED if hasattr(nearest_barrel, 'vel_y') else 0.0
        else:
            barrel_x = barrel_y = barrel_vel_x = barrel_vel_y = 0.0
        #return [norm_x, norm_y, grounded, on_ladder, climbing, ladder_x, barrel_x, barrel_y, barrel_vel_x, barrel_vel_y, distance_to_princess_y]

        return [norm_x, norm_y, grounded, on_ladder, climbing, ladder_x, barrel_x, barrel_y]