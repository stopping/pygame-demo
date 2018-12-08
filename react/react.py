from collections import deque

class Rx:
  updated = set()
  locked = False

  @staticmethod
  def lock():
    Rx.locked = True

  @staticmethod
  def unlock():
    Rx.unlocked = False
    Rx.propagate()

  def __init__(self):
    self.upstream = set()
    self.downstream = set()
    self.val = None

  def __call__(self):
    return self.val

  def update(self):
    raise NotImplementedError()

  @staticmethod
  def propagate():
    sorted = deque()
    unmarked = set()
    new = Rx.updated
    while len(new) > 0:
      el = new.pop()
      for d in el.downstream:
        if d in unmarked:
          continue
        new.add(d)
      unmarked.add(el)
    marked = set()
    def visit(n):
      if n in marked:
        return
      for d in n.downstream:
        visit(d)
      unmarked.discard(n)
      marked.add(n)
      sorted.appendleft(n)
    while len(unmarked) > 0:
      visit(unmarked.pop())
    while len(sorted) > 0:
      sorted.popleft().update()

# Create a node whose value is returned by a function |f| and a list of bound
# arguments. |argv| is a list of Rx parameters.
class Bind(Rx):
  def __init__(self, f, *argv):
    self.argv = argv
    self.upstream = set(self.argv)
    self.downstream = set()
    self.f = f
    for up in self.upstream:
      up.downstream.add(self)

  def update(self):
    if self.f is None:
      return;
    evaluated = [arg() for arg in self.argv]
    self.val = self.f(*evaluated)


class Auto(Rx):
  calculating_deps = False
  deps = set()
  updated = set()
  locked = False

  def __init__(self, expr):
    Auto.calculating_deps = True
    Auto.deps = set()
    self.expr = expr
    self.val = self.expr()
    self.downstream = set()
    self.upstream = Auto.deps
    for dep in self.upstream:
      dep.downstream.add(self)
    Auto.deps = set()
    Auto.calculating_deps = False

  def update(self):
    if self.expr is None:
      return;
    self.val = self.expr()

  def __call__(self):
    if Auto.calculating_deps:
      Auto.deps.add(self)
    return self.val

class Val(Rx):
  def __init__(self, val):
    Rx.__init__(self)
    self.val = val

  MISSING = object()
  def __call__(self, val=MISSING):
    if val is Val.MISSING:
      return self.val
    self.val = val
    Rx.updated.add(self)
    if Rx.locked:
      return
    Rx.propagate()

  def update(self):
    pass
