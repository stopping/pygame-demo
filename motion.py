movers = []

X = 0
Y = 1
Z = 2

# Component for entity motion
class Motion:

  DIRECTIONS = [X, Y, Z]

  def __init__(self, static=False):
    self.pos = [0, 0, 0]
    self.vel = [0, 0, 0]
    self.last_pos = list(self.pos)
    self.static = static
    if not self.static:
      movers.append(self)

  def update(self, dt):
    self.last_pos = self.pos
    self.pos = [a + b * dt for a, b in zip(self.pos, self.vel)]

def update(dt):
  for m in movers:
    m.update(dt)
