def create_integrator(init=None):
  accum = init
  x_last = None
  t_last = None
  called_once = False
  def integrator(x, t):
    nonlocal accum, x_last, t_last, called_once
    if called_once:
      # trapezoidal rule
      accum = accum + (x + x_last) * (t - t_last) / 2
    else:
      called_once = True
      if accum is None:
        accum = x * 0
    x_last = x
    t_last = t
    return accum
  return integrator

def linear(init=0):
  val = init
  t_last = None
  called_once = False
  def func(target, vel, t):
    nonlocal val, t_last, called_once
    if not called_once:
      called_once = True
      t_last = t
      return val
    if target > val:
      val += vel * (t - t_last)
      val = min(val, target)
    elif target < val:
      val -= vel * (t - t_last)
      val = max(val, target)
    t_last = t
    return val
  return func

