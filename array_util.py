
def add(*arrs):
  def arr_add_2(arr1, arr2):
    if len(arr1) > len(arr2):
      big = list(arr1)
      small = arr2
    else:
      big = list(arr2)
      small = arr1
    for i in range(len(small)):
      big[i] += small[i]
    return big
  accum = arrs[0]
  for arr in arrs[1:]:
    accum = arr_add_2(accum, arr)
  return accum

def offset(arr, amount):
  return [x + amount for x in arr]
