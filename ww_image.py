import tkinter as tk
# from PIL import Image, ImageTk, ImageDraw

class ZoomedCanvas(tk.Canvas):
    def __init__(self, master=None, NE=(0,0), width=50, height=50):
        super().__init__(master, width=width*2, height=height*2)
        self.create_rectangle(10, 10, 11, 11, outline='green')



# class RollingImage():
#     def __init__(self, size):
#         self.im = Image.new(mode='RGB', size=size)
#         self.image = ImageTk.PhotoImage(self.im)
#         # self.image = ImageTk.PhotoImage(image="RGB", size=size)
#         # self.image = tk.PhotoImage(master=root, data=Image.new(mode='RGB', size=size))
#         pass
#
# # root = tk.Tk()
# test = RollingImage((10,10))
# # label = tk.Label(image=test.image)
# # label.image = test.image
# # label.pack()
# # root.mainloop()

# root = tk.Tk()
# im = Image.new(mode='RGB', size=(100,100))
# pim = ImageTk.PhotoImage(im)
# draw = ImageDraw.Draw(im)
# draw.rectangle([0, 0, 40, 40], fill="green")
# del draw
# label = tk.Label(image=pim)
# label.pack()
# pim.paste(im)
# root.mainloop()

root = tk.Tk()
can = ZoomedCanvas(root)
can.pack()
tk.mainloop()