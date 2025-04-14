import os
import pygame
from projekt.config import *
import time

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, platforms, borders, ladders):
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

    def move_left(self):
        self.x -= self.speed
        #self.vel_y += self.gravity
        #self.y += self.vel_y

        self.rect.x = self.x
        #self.rect.y = self.y

    def move_right(self):
        self.x += self.speed
        #self.vel_y += self.gravity
        #self.y += self.vel_y

        self.rect.x = self.x
        #self.rect.y = self.y

    def move_up(self):
        self.y -= self.speed
        self.vel_y += self.gravity
        self.y += self.vel_y

        self.rect.x = self.x
        self.rect.y = self.y

    def move_down(self):
        self.y += self.speed
        self.vel_y += self.gravity
        self.y += self.vel_y

        self.rect.x = self.x
        self.rect.y = self.y

    def upup(self):
        self.vel_y = -self.jump

    def move(self, keys):
        prev_y = self.y
        prev_x = self.x

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_right()

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
                    # self.can_jump = False  # AKO PUKNE I OVO JE RAZLOG
                # snapanje igraca na platformu ako pada
                elif (prev_y + self.height <= platform.rect.top and
                      self.rect.bottom >= platform.rect.top and
                      self.vel_y >= 0):
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.rect.y = self.y
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
                #padanje i provjera
                if prev_y + self.height <= platform.rect.top:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                #provjera da se ne probije platforma, odozdo
                elif prev_y >= platform.rect.bottom:
                    self.y = platform.rect.bottom
                    self.vel_y = 0

                #odbijanje od bordera
                if prev_x + self.width <= platform.rect.left:
                    self.x = platform.rect.left - self.width
                elif prev_x >= platform.rect.right:
                    self.x = platform.rect.right

                self.rect.x = self.x
                self.rect.y = self.y

    def on_ladder(self):
        '''for ladder in self.ladders:
            if self.rect.colliderect(ladder.rect):
                return True'''
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
        prev_y, prev_x = self.y, self.x
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
        self.check_collision_border(self.borders, prev_x)

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
        return [norm_x, norm_y, grounded, on_ladder, climbing, ladder_x, barrel_x, barrel_y, barrel_vel_x, barrel_vel_y, distance_to_princess_y]