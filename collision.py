from base import Bounds
from motion import Motion

import draw

static_colliders = []
dynamic_colliders = []

# Axis-aligned Bounding-box collider
class Collider:
  def __init__(self, motion, bounds):
    self.motion = motion
    self.bounds = bounds
    if self.motion.static:
      static_colliders.append(self)
    else:
      dynamic_colliders.append(self)

  def collide(self, other):
    raise NotImplementedError

  def draw(self, surface):
    position = self.motion.pos
    bounds = self.bounds
    left = (position[Motion.X] + bounds[Motion.X].lo) * draw.BLOCK_WIDTH + map_offset[0]
    top = (position[Motion.Y] + bounds[Motion.Y].lo) * draw.BLOCK_DEPTH + map_offset[1]
    width = bounds[Motion.X].size() * draw.BLOCK_WIDTH
    height = bounds[Motion.Y].size() * draw.BLOCK_DEPTH
    rect = pygame.Rect(left, top, width, height)
    pygame.draw.rect(surface, pygame.Color('red'), rect, 1)


class StaticCollider(Collider):
  def __init__(self, motion, bounds):
    super().__init__(motion, bounds)

  def collide(self, other):
    pass

class ConformalCollider(Collider):
  def __init__(self, motion, bounds):
    super().__init__(motion, bounds)

  def collide(self, other):
    self.collide_simple(other)

  def collide_simple(self, other):
    smallest_overlap = 100
    best_dir = None
    for d in Motion.DIRECTIONS:
      my_bounds = self.bounds[d].shift(self.motion.pos[d])
      other_bounds = other.bounds[d].shift(other.motion.pos[d])
      overlap = my_bounds.overlap(other_bounds)
      if overlap is None:
        # No collision
        return
      if overlap < smallest_overlap:
        best_dir = d
        smallest_overlap = overlap
    if best_dir is None:
      return
    # Determine if we overlap on the low or high side
    my_bounds = self.bounds[best_dir].shift(self.motion.pos[best_dir])
    other_bounds = other.bounds[best_dir].shift(other.motion.pos[best_dir])
    from_hi = other_bounds.hi - my_bounds.lo
    from_lo = my_bounds.hi - other_bounds.lo
    if self.motion.vel[best_dir] > 0:
      self.motion.pos[best_dir] -= my_bounds.hi - other_bounds.lo + 0.01
    else:
      self.motion.pos[best_dir] += other_bounds.hi - my_bounds.lo + 0.01

  def collide_adv(self, other):
    # Make this class conform to the bounds of the other's hitbox.
    # For each direction, if the object would have passed through the
    # boundary, reset it so that the boundaries simply touch.
    # For each direction, determine when the collision will occur.
    # Pick the soonest dimension which will collide and then arrest the
    # motion in that direction.
    best_frac = 2
    best_dir = None
    for d in Motion.DIRECTIONS:
      if self.motion.vel[d] > 0:
        # self.hi will collide with other.lo
        intersect = other.bounds[d].lo + other.motion.pos[d]
        begin = self.bounds[d].hi + self.motion.last_pos[d]
        end = self.bounds[d].hi + self.motion.pos[d]
        frac = 0
        if end != begin:
          frac = (intersect - begin) / (end - begin)
        if 0 <= frac <= 1 and frac < best_frac:
          # Check for intersection in other dimensions. Remaining bounds
          # must overlap in order for there to be a collision.
          collided = True
          for d_other in Motion.DIRECTIONS:
            if d is d_other:
              continue
            delta = self.motion.pos[d_other] - self.motion.last_pos[d_other]
            interp = delta * frac + self.motion.last_pos[d_other]
            if not self.bounds[d_other].shift(interp).overlaps_with(other.bounds[d_other].shift(other.motion.pos[d_other])):
              collided = False
          if collided:
            best_frac = frac
            best_dir = d
      elif self.motion.vel[d] < 0:
        intersect = other.bounds[d].hi + other.motion.pos[d]
        begin = self.bounds[d].lo + self.motion.last_pos[d]
        end = self.bounds[d].lo + self.motion.pos[d]
        frac = 0
        if end != begin:
          frac = (intersect - begin) / (end - begin)
        if 0 <= frac <= 1 and frac < best_frac:
          # Check for intersection in other dimensions. Remaining bounds
          # must overlap in order for there to be a collision.
          collided = True
          for d_other in Motion.DIRECTIONS:
            if d is d_other:
              continue
            delta = self.motion.pos[d_other] - self.motion.last_pos[d_other]
            interp = delta * frac + self.motion.last_pos[d_other]
            if not self.bounds[d_other].shift(interp).overlaps_with(other.bounds[d_other].shift(other.motion.pos[d_other])):
              collided = False
          if collided:
            best_frac = frac
            best_dir = d
    if best_dir is None:
      return
    print('Collision in direction {}!'.format(best_dir))
    # There was a collision.
    if self.motion.vel[best_dir] > 0:
      self.motion.pos[best_dir] = \
          other.motion.pos[best_dir] + other.bounds[best_dir].lo - self.bounds[best_dir].hi - 0.01
    elif self.motion.vel[best_dir] < 0:
      self.motion.pos[best_dir] = \
          other.motion.pos[best_dir] + other.bounds[best_dir].hi - self.bounds[best_dir].lo + 0.01
    else:
      print('We did not reset the position')

def update():
  for d in dynamic_colliders:
    for s in static_colliders:
      d.collide(s)
