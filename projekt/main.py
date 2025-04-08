import pygame
from projekt.config import *
from game import Game

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Donkey Kong")

if __name__ == "__main__":
    game = Game(screen)
    #game.run_neat(game.config_path)
    game.run()
    #game.run_winner()