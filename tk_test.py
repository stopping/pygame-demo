#!/usr/bin/python3

from tkinter import *
from PIL import *

tk = Tk()

path='/mnt/c/Users/Sean/Dropbox/game/graphics/scenes/test_sheet.png'

can = Canvas(tk)
can.pack()
img = PhotoImage(file=path)
can.create_image(0, 0, anchor=NW, image=img)

# Last line
tk.mainloop()
