import pygame
from projekt.config import *

class Princess(pygame.sprite.Sprite):

    def __init__(self, x, y, player):
        super().__init__()

        self.x = x
        self.y = y
        self.player = player

        self.width = PRINCESS_WIDTH
        self.height = PRINCESS_HEIGHT

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((251, 198, 207))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))


    def draw(self, screen):
        screen.blit(self.image, self.rect)