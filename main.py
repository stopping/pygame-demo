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
#screen = pygame.display.set_mode(tuple(window_res))
screen = pygame.display.set_mode(tuple(window_res), (
    pygame.DOUBLEBUF))

running = True

surface = pygame.Surface(tuple(window_res / zoom))

m = Map()
e = Editor()
#e.parse_from_file('collision_map.txt')
e.parse_from_file('map.txt')
world = e.features['world']

c = clock.Clock()
c.tick(pygame.time.get_ticks())

player = Player(2, 2)

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    player.handle_event(event)
  if not running:
    break
  c.tick(pygame.time.get_ticks())
  dt = c.dt()
  motion.update(dt)
  fps = 0
  if dt != 0:
    fps = 1 / dt
  print(int(fps))
  for (loc, block) in world.blocks.items():
    for obj in block.objects:
      player.map_obj.collider.collide(obj.collider)
  surface.fill((0,0,0))
  m.draw(surface, world, player, c.time)
  pygame.transform.scale(surface, tuple(window_res), screen)
  #pygame.display.update(pygame.Rect((0, 0), (600, 400)))
  pygame.display.update()

pygame.quit()
sys.exit()
