from base import Bounds
from draw import DrawObject

import collections
import copy
import map_object
import motion
import re

X = 0
Y = 1
Z = 2

class ZoneAttributes:
  def __init__(self):
    # map of zone label to floor label
    self.floors = {}
    self.outer = {}
    self.height = 1

class Block:
  def __init__(self):
    self.objects = []
    self.coords = None

# A feature is a set of occupied blocks.
class Feature:
  def __init__(self, name):
    self.name = name
    # Block features
    self.blocks = collections.defaultdict(Block)

  def write(self, zone_buffer, zone_attr, location):
    if len(zone_buffer) is 0:
      return
    cursor = list(location)

    # Write floor tiles
    for j in range(len(zone_buffer)):
      cursor[Y] = location[Y] + j
      for i in range(len(zone_buffer[j])):
        cursor[X] = location[X] + i
        self.write_floor(cursor, zone_buffer[j][i], zone_attr)

    cursor = list(location)
    for k in range(zone_attr.height):
      cursor[Z] = location[Z] + k
      # Top wall
      j = 0
      cursor[Y] = 0
      for i in range(len(zone_buffer[j])):
        cursor[X] = location[X] + i
        self.write_wall(cursor, zone_buffer[j][i], zone_attr, 'u')

      # Bottom wall
      j = -1
      cursor[Y] = len(zone_buffer) - 1
      for i in range(len(zone_buffer[j])):
        cursor[X] = location[X] + i
        self.write_wall(cursor, zone_buffer[j][i], zone_attr, 'd')

      # Left wall
      i = 0
      cursor[X] = 0
      for j in range(len(zone_buffer)):
        cursor[Y] = location[Y] + j
        self.write_wall(cursor, zone_buffer[j][i], zone_attr, 'l')

      # Right wall
      i = -1
      cursor[X] = len(zone_buffer[0]) - 1
      for j in range(len(zone_buffer)):
        cursor[Y] = location[Y] + j
        self.write_wall(cursor, zone_buffer[j][i], zone_attr, 'r')

  def write_wall(self, cursor, zone_label, zone_attr, wall_type):
    if zone_label not in zone_attr.outer:
      return
    offset_map = {
        'u': [0, 0, 0],
        'l': [0, 0, 0],
        'd': [0, 1, 0],
        'r': [1, 0, 0],
    }

    bounds_map = {
        'u': [Bounds(0, 1), Bounds(0, 0), Bounds(0, 1)],
        'l': [Bounds(0, 0), Bounds(0, 1), Bounds(0, 1)],
        'd': [Bounds(0, 1), Bounds(0, 0), Bounds(0, 1)],
        'r': [Bounds(0, 0), Bounds(0, 1), Bounds(0, 1)],
    }

    wall_motion = motion.Motion(True)
    block_offset = offset_map[wall_type]
    wall_motion.pos = [a + b for a, b in zip(block_offset, list(cursor))]
    draw_obj = None
    if wall_type is 'u' or wall_type is 'd':
      draw_obj = DrawObject(wall_motion,
                            zone_attr.outer[zone_label],
                            DrawObject.X)
    if wall_type is 'l' or wall_type is 'r':
      draw_obj = DrawObject(wall_motion,
                            zone_attr.outer[zone_label],
                            DrawObject.Y)
    map_obj = map_object.MapObject(wall_motion,
                                   bounds_map[wall_type],
                                   block_offset,
                                   draw_obj)
    block = self.blocks[tuple(cursor)]
    block.coords = tuple(cursor)
    block.objects.append(map_obj)

  def write_floor(self, cursor, zone_label, zone_attr):
    if zone_label not in zone_attr.floors:
      return
    floor_motion = motion.Motion(True)
    floor_motion.pos = list(cursor)
    block_offset = [0, 0, 0]
    draw_obj = DrawObject(floor_motion,
                          zone_attr.floors[zone_label],
                          DrawObject.FLOOR)
    floor_bounds = [Bounds(0, 1), Bounds(0, 1), Bounds(-0.05, 0.05)]
    map_obj = map_object.MapObject(
        floor_motion, floor_bounds, block_offset, draw_obj)
    block = self.blocks[tuple(cursor)]
    block.coords = tuple(cursor)
    block.objects.append(map_obj)

  def copy_block(self, cursor, block):
    new_block = copy.deepcopy(block)
    new_block.coords = tuple(cursor)
    self.blocks[tuple(cursor)] = new_block
    for obj in new_block.objects:
      old_pos = obj.block_offset
      obj.motion.pos = [a + b for a,b in zip(obj.block_offset, cursor)]

  def stamp(self, stamp, c):
    for (loc, block) in stamp.blocks.items():
      new_loc = [loc[0] + c[0], loc[1] + c[1], loc[2] + c[2]]
      self.copy_block(new_loc, block)

# An editor environment consists of:
# * Namespaces
# * - Features
class Editor:
  def __init__(self):
    self.namespaces = {}
    self.features = {}
    self.namespace = ''
    self.curr_feature = None
    self.cursor = (0,0,0)
    self.zone_attr = ZoneAttributes()
    self.zone_buffer = []

  def parse_from_file(self, fn):
    cmd_dict = {
        'feature': self.edit_feature,
        'ns': self.set_namespace,
        'abs': self.abs,
        'rel': self.rel,
        'height': self.height,
        'floor': self.set_floor,
        'outer': self.set_outer,
        'w': self.write,
        'stamp': self.stamp,
    }
    file = open(fn, 'r')
    for raw_line in file:
      line = raw_line.rstrip()
      # Discard empty lines or comments
      if len(line) is 0 or line[0] is '#':
        continue
      # First check if it's an editor command.
      if line[0] is ':':
        cmd_match = re.match(r'^:(\w+)(.+)?', line)
        if not cmd_match:
          continue
        cmd = cmd_match.group(1)
        has_args = bool(cmd_match.group(2))
        args = []
        if has_args:
          args = cmd_match.group(2).split()
        if cmd not in cmd_dict:
          continue
        cmd_dict[cmd](*args)
        continue
      # Use current mode to determine key actions. Only the 'edit'
      # action is currently supported.
      self.handle_edit(line)

  def edit_feature(self, name):
    if name not in self.features:
      self.features[name] = Feature(name)
    self.curr_feature = self.features[name]
    self.zone_attr = ZoneAttributes()
    self.zone_buffer.clear()

  def set_namespace(self, ns=''):
    self.namespace = ns

  def abs(self, x, y, z):
    self.cursor = (int(x), int(y), int(z))

  def rel(self, x, y, z):
    self.cursor = tuple(map(lambda a, b: int(a) + int(b), self.cursor, (x, y, z)))

  def height(self, height):
    self.zone_attr.height = int(height)

  def set_floor(self, zone, floor):
    self.zone_attr.floors[zone] = floor

  def set_outer(self, zone, outer):
    self.zone_attr.outer[zone] = outer

  def write(self):
    self.curr_feature.write(self.zone_buffer, self.zone_attr, self.cursor)

  def stamp(self, stamp_name):
    if stamp_name not in self.features:
      return
    stamp = self.features[stamp_name]
    self.curr_feature.stamp(stamp, self.cursor)

  def handle_edit(self, line):
    self.zone_buffer.append(line)
