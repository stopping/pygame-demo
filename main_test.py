from draw import Map
from editor import Editor
from player import Player

import clock
import collections
import collision
import motion
import numpy as np
import pygame
import re
import react.react as r
import sys

window_res = np.array((1600, 900))
zoom = 3

pygame.init()
screen = pygame.display.set_mode(tuple(window_res))

running = True

surface = pygame.Surface(tuple(window_res / zoom))

m = Map()
e = Editor()
#e.parse_from_file('collision_map.txt')
e.parse_from_file('map.txt')
world = e.features['world']

c = pygame.time.Clock()

player = Player(2, 2)

pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    player.handle_event(event)
  if not running:
    break
  print(c.get_fps())
  rect = pygame.Rect((0,0), (10,10))
  pygame.display.update(rect)
  c.tick(1000)

pygame.quit()
sys.exit()
