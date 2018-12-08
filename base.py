class Bounds:
  def __init__(self, lo=0, hi=0):
    self.lo = lo
    self.hi = hi

  def shift(self, shift):
    return Bounds(shift + self.lo, shift + self.hi)

  def overlaps_with(self, other):
    return self.lo <= other.hi and self.hi >= other.lo

  def size(self):
    return self.hi - self.lo

  # Return the size of the overlap
  def overlap(self, other):
    if not self.overlaps_with(other):
      return None
    smaller = min(self.size(), other.size())
    return min(self.hi - other.lo, other.hi - self.lo, smaller)

