import pygame

class Coin(pygame.sprite.Sprite):
    coin_positions = [
        (350, 700, 20, 20),
        (550, 680, 20, 20),
        (630, 640, 20, 20)
    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(topleft=(x, y))