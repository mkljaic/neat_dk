import pygame as py
py.font.init()

#=================== Game and Screen Config ==================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

BORDER_HEIGHT = 1280
BORDER_WIDTH = 400

FPS = 30

PLAYER_SPEED = 2            # PLAYER_SPEED = 2 + 4
PLAYER_JUMP = 8            # PLAYER_JUMP = 8 + 5

PLAYER_HOR_VELOCITY = 0
PLAYER_VER_VELOCITY = 0

GRAVITY = 0.5

PLAYER_WIDTH = 20
PLAYER_HEIGHT = 30

PLAYER_X = 100
PLAYER_Y = 680

BARREL_WIDTH = 20
BARREL_HEIGHT = 20

BARREL_X = 100
BARREL_Y = 220

BARREL_SPEED = 5

PRINCESS_WIDTH = 20
PRINCESS_HEIGHT = 40

PRINCESS_X = 280
PRINCESS_Y = 129

#=================== NEAT / Neural Network Constants ==================================
INPUT_NEURONS = 11
OUTPUT_NEURONS = 3

NODE_RADIUS = 20
NODE_SPACING = 5
LAYER_SPACING = 100
CONNECTION_WIDTH = 1

#=================== Colors and Fonts ==================================
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
DARK_RED = (100, 0, 0)
RED_PALE = (250, 200, 200)
DARK_RED_PALE = (150, 100, 100)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
GREEN_PALE = (200, 250, 200)
DARK_GREEN_PALE = (100, 150, 100)
BLUE = (0, 0, 255)
BLUE_PALE = (200, 200, 255)
DARK_BLUE = (100, 100, 150)

NODE_FONT = py.font.SysFont("comicsans", 15)
STAT_FONT = py.font.SysFont("comicsans", 50)

#=================== Enumerations ==================================
INPUT = 0
MIDDLE = 1
OUTPUT = 2
