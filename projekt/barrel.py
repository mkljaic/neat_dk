import pygame
from projekt.config import *

class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y, platforms, borders):
        super().__init__()

        self.x = x
        self.y = y

        self.width = BARREL_WIDTH
        self.height = BARREL_HEIGHT

        self.vel_x = BARREL_SPEED
        self.vel_y = 0

        self.platforms = platforms
        self.borders = borders

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((88, 57, 39))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def move_barrel(self):
        prev_y = self.y
        prev_x = self.x

        self.x += self.vel_x

        self.vel_y += GRAVITY
        self.y += self.vel_y

        self.rect.x = self.x
        self.rect.y = self.y

        return prev_y, prev_x

    def check_collision_border(self, prev_x):
        for border in self.borders:
            if self.rect.colliderect(border.rect):
                if border.rect.width < border.rect.height:
                    if prev_x + self.width <= border.rect.left:
                        self.x = border.rect.left - self.width
                        self.vel_x = -self.vel_x
                    elif prev_x >= border.rect.right:
                        self.x = border.rect.right
                        self.vel_x = -self.vel_x
                    self.rect.x = self.x

    def platform_collision(self):
        for platform in self.platforms:
            if self.rect.colliderect(platform.rect):
                if self.y + self.height <= platform.rect.top + 10 and self.vel_y >= 0:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.rect.y = self.y

    def update_barrel(self):
        prev_y, prev_x = self.move_barrel()
        self.check_collision_border(prev_x)
        self.platform_collision()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def get_state(self):
        return [self.rect.x, self.rect.y, self.vel_x, self.vel_y]
