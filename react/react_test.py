from react import Auto, Bind, Val
import math

def new_integrator():
  accum = 0
  x_last = None
  t_last = None
  called_once = False
  def integrator(x, t):
    nonlocal accum, x_last, t_last, called_once
    if called_once:
      # trapezoidal rule
      add = (x + x_last) * (t - t_last) / 2
      accum += add
    else:
      called_once = True
    x_last = x
    t_last = t
    return accum
  return integrator

t = Val(0)
x = Bind(lambda a : math.cos(2 * math.pi * a), t)
y = Bind(lambda a : math.sin(2 * math.pi * a), t)

area = Bind(new_integrator(), y, x)

for step in range(100):
  t(t() + 0.005)
print(area())
