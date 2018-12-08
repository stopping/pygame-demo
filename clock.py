import collections

max_history_len = 10

class Clock:
  def __init__(self):
    self.time = 0
    self.history = collections.deque()

  def tick(self, ticks_ms):
    self.history.appendleft(self.time)
    while len(self.history) > max_history_len:
      self.history.pop()
    self.time = ticks_ms / 1000

  def last_time(self):
    return self.history[0]

  def dt(self):
    return self.time - self.last_time()

