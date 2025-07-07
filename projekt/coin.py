import pygame

class Coin(pygame.sprite.Sprite):
    coin_positions = [
        (350, 700, 20, 20), #prvi
        #(550, 680, 20, 20), #onaj na ljestvama
        (640, 675, 20, 20), #niski
        (620, 620, 20, 20),  # onaj gore da im kaze da idu lijevo
        (600, 620, 20, 20),  # onaj drugi gore da im kaze da idu lijevo
        (630, 620, 20, 20),  # onaj skroz desno
        (640, 620, 20, 20),  # onaj skroz desno
        (580, 625, 20, 20), #onaj gore
        (550, 600, 20, 20),  # da ih usmjeri na pravi put
        (450, 600, 20, 20)  # da ih usmjeri na pravi put
    ]

    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(topleft=(x, y))