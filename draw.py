from base import Bounds
from motion import *

import array_util as arr_util

import calculus
import camera
import heapq
import numpy as np
import pygame
import random

# map to col, row in sprite sheet
tiles_map = {
    'b': 0,
    'c': 1,
    'f': 0,
    'g': 1,
    }

# Sprite sheet
WALL_PITCH_X = 24
WALL_PITCH_Y = 32
FLOOR_PITCH_X = 48
FLOOR_PITCH_Y = 16

BLOCK_WIDTH = 48
BLOCK_HEIGHT = 24
BLOCK_DEPTH = 16

floor_dim = np.array((48, 16))
wall_dim = np.array((48, 24))

path='iso_sheet.png'
img = pygame.image.load(path)

class DrawObject:
  # Orientation in space. All objects are "cut outs"
  FLOOR = 0
  X = 1
  Y = 2
  DIAGONAL = 3

  def __init__(self, motion, label, orientation):
    self.motion = motion
    self.label = label
    self.orientation = orientation

def extend_range(r, v):
  if v < r[0]:
    r[0] = v
  if v > r[1]:
    r[1] = v

def pos2px(pos):
  return [
    int((pos[X] - pos[Y]) * BLOCK_WIDTH / 2),
    int((pos[X] + pos[Y]) * BLOCK_DEPTH / 2 - pos[Z] * BLOCK_HEIGHT)
  ]

class Map:
  def __init__(self):
    self.alpha_tmp = pygame.Surface((48, 32)).convert()
    self.faders = {}
    self.x_range = [0, 0]
    self.y_range = [0, 0]
    self.z_range = [0, 0]
    self.camera = camera.Camera()

  def draw(self, surface, world, player, time):
    objects_map = {}
    uid = 0
    draw_objects = []
    # Priority algorithm for walls and floors
    for (loc, block) in world.blocks.items():
      for map_obj in block.objects:
        draw_obj = map_obj.draw_obj
        if draw_obj is None:
          continue
        (x, y, z) = draw_obj.motion.pos
        extend_range(self.x_range, loc[0])
        extend_range(self.y_range, loc[1])
        extend_range(self.z_range, loc[2])
        grid_priority = x + y + 20 * z
        objects_map[uid] = draw_obj
        draw_objects.append((grid_priority, uid))
        uid += 1

    heapq.heapify(draw_objects)

    map_offset_px = [
      int(self.y_range[1] * BLOCK_WIDTH / 2),
      # Add 1 to the z range to include the height of the top block
      int((self.z_range[1] + 1) * BLOCK_HEIGHT)
    ]

    camera.motion.pos = list(player.motion.pos)
    cam_offset_px = pos2px(camera.motion.pos)

    while draw_objects:
      obj_id = heapq.heappop(draw_objects)[1]
      draw_obj = objects_map[obj_id]
      if draw_obj.label not in tiles_map:
        continue
      obj_px = pos2px(draw_obj.motion.pos)
      sheet_row = tiles_map[draw_obj.label]
      if draw_obj.orientation is DrawObject.FLOOR:
        sheet_offset = [4 * 24, sheet_row * FLOOR_PITCH_Y]
        draw_offset_px = [-24, 0]
        sprite_dim = [FLOOR_PITCH_X, FLOOR_PITCH_Y]
      if draw_obj.orientation is DrawObject.X:
        sheet_offset = [0 * 24, sheet_row * WALL_PITCH_Y]
        draw_offset_px = [0, -24]
        sprite_dim = [WALL_PITCH_X, WALL_PITCH_Y]
      if draw_obj.orientation is DrawObject.Y:
        sheet_offset = [1 * 24, sheet_row * WALL_PITCH_Y]
        draw_offset_px = [-24, -24]
        sprite_dim = [WALL_PITCH_X, WALL_PITCH_Y]

      sheet_rect = pygame.Rect(sheet_offset, sprite_dim)
      """
      fade_target = 0
      if obj_id not in self.faders:
        self.faders[obj_id] = calculus.linear(0)
      fade = self.faders[obj_id](fade_target, 5, time)
      x_final = x_px + map_offset[0] + draw_offset_px[0]
      y_final = y_px + map_offset[1] + draw_offset_px[1]
      self.alpha_tmp.blit(surface, (-x_final , -y_final))
      self.alpha_tmp.blit(img, (0,0), sheet_rect)
      self.alpha_tmp.set_alpha(255 - (255-64) * fade)
      surface.blit(self.alpha_tmp, (x_final, y_final))
      """
      final_px = arr_util.add(obj_px, map_offset_px, draw_offset_px)
      surface.blit(img, tuple(final_px), sheet_rect)
    player_radius = 6
    player_px = pos2px(player.motion.pos)

    final_player_px = arr_util.add(player_px, map_offset_px)
    # Draw player
    pygame.draw.circle(surface, (255, 0, 0), tuple(final_player_px), player_radius)
