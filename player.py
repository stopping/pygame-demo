from base import Bounds
from motion import *

import calculus
import map_object
import numpy
import pygame

# Tiles per second
velocity = 3

class Player:
  def __init__(self, x, y):
    self.motion = Motion(False)
    width = Bounds(-0.1, 0.1)
    bounds = [width, width, width]
    self.motion.pos[X] = x
    self.motion.pos[Y] = y
    self.motion.pos[Z] = 0.5
    self.map_obj = map_object.MapObject(self.motion, bounds)

  def handle_event(self, event):
    if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
      return
    key_down = event.type is pygame.KEYDOWN
    key_up = event.type is pygame.KEYUP
    vel = self.motion.vel
    if event.key == pygame.K_w:
      vel[Y] += velocity * (key_up - key_down)
    if event.key == pygame.K_a:
      vel[X] += velocity * (key_up - key_down)
    if event.key == pygame.K_s:
      vel[Y] += velocity * (key_down - key_up)
    if event.key == pygame.K_d:
      vel[X] += velocity * (key_down - key_up)
