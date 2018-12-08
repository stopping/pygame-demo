import collision

class MapObject:
  def __init__(self, motion, bounds, block_offset=[0,0,0], draw_obj=None):
    self.motion = motion
    self.block_offset = block_offset
    if motion.static:
      self.collider = collision.StaticCollider(self.motion, bounds)
    else:
      self.collider = collision.ConformalCollider(self.motion, bounds)
    self.draw_obj = draw_obj
    self.data = {}
