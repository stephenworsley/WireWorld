import wireworld as ww
import tkinter as tk
from tkinter import  messagebox


# TODO generate dictionaries for an arbitrary number of states, perhaps with matplotlib colormaps
colordict = {0: 'white', 1: 'red', 2: 'blue', 3: 'yellow'}
nightdict = {0: 'black', 1: 'red', 2: 'blue', 3: 'yellow'}


class Grid(tk.Frame):
    '''Generates the wireworld GUI.'''
    def __init__(self, world, master=None, size=None):
        super().__init__(master)
        self.pack()
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(side= 'top')

        self.palette = colordict
        if size is None:
            self.size = world.size
        else:
            self.size = size
        self.world = world
        self.display_world()

        self.update_button = tk.Button(self, text='Update', command=self.update)
        self.update_button.pack(side = 'left')
        self.run_button = tk.Button(self, text='Run', command=self.run)
        self.run_button.pack(side = 'left')
        self.pause_button = tk.Button(self, text='Pause', command=self.pause)
        self.pause_button.pack(side= 'left')
        self.running = False

        self.p_switch =tk.Button(self, text='Night mode', command=self.n_mode)
        self.p_switch.pack(side='left')

        self.delay = tk.IntVar()
        self.delay.set(500)
        self.delay_entry = tk.Entry(textvariable=self.delay, width=6)
        self.delay_label = tk.Label(text='Delay')
        self.delay_label.pack(side='left')
        self.delay_entry.pack(side='left')

        self.file_button = tk.Button(self, text='Load/Save', command=self.open_file_window)
        self.file_button.pack(side='right')

    def coord_map(self, coord):
        '''Maps from a coordinate on the button array to a coordinate on the world.'''
        w_coord = (coord[0]+ self.grid_NE[0], coord[1], self.grid_NE[1])
        return w_coord

    def display_world(self):
        '''Initialises buttons based on world data.'''
        self.grid_NE = (0,0)
        self.button_array = []
        for x in range(self.size[0]):
            row = []
            for y in range(self.size[1]):
                w_coord = self.coord_map((x,y))
                color = self.getcolor(w_coord)
                button = tk.Button(self.grid_frame, relief="raised", bg=color,
                                   activebackground=color, command=self.command_generator((x,y)))
                button.grid(row=x, column=y)
                row.append(button)
            self.button_array.append(row)


    def getcolor(self, coord):
        '''Returns the color associated with the specified state.'''
        state = self.world.getcoordstate(coord)
        color = self.palette[state]
        return color

    def command_generator(self, coord):
        '''Generates a command to update the button in the specified position.'''
        def command():
            w_coord = self.coord_map(coord)
            self.world.editpoint(w_coord)
            color = self.getcolor(w_coord)
            x,y = coord
            self.button_array[x][y].config(bg=color, activebackground=color)
        return command

    def refresh(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                w_coord = self.coord_map((x,y))
                color = self.getcolor(w_coord)
                self.button_array[x][y].config(bg=color, activebackground=color)

    def update(self):
        '''Updates the cellular automata.'''
        self.world.step()
        self.refresh()

    def run(self):
        '''Starts the run loop.'''
        self.running = True
        self.update()
        self.after(self.delay.get(), self.runcheck)

    def runcheck(self):
        '''Recursively calls the run function unless the app has been paused.'''
        if self.running:
            self.run()

    def pause(self):
        '''Stops the run loop.'''
        self.running = False

    def open_file_window(self):
        '''Opens a window with load and save options.'''
        self.pause()
        self.window = tk.Toplevel(self)
        self.window.grab_set()
        self.file_label = tk.Label(self.window, text='File name')
        self.file_label.grid(row=0, column=0)
        self.file_name = tk.StringVar('')
        self.file_entry = tk.Entry(self.window, textvariable=self.file_name)
        self.file_entry.grid(row=0, column=1)
        self.load_button = tk.Button(self.window, text='Load', command=self.load)
        self.load_button.grid(row=1, column=0)
        self.save_button = tk.Button(self.window, text='Save', command=self.save)
        self.save_button.grid(row=1, column=1, sticky='W')

    def load(self):
        '''Attempts to load and display world data from file.'''
        try:
            world = ww.load_world(self.file_name.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self.world = world
        self.size = self.world.size
        for x in self.button_array:
            for y in x:
                y.destroy()
        self.display_world()
        self.window.destroy()

    def save(self):
        '''Attempts to save world data to file.'''
        world = self.world
        try:
            ww.save_world(world, self.file_name.get(), permission='x')
        except FileExistsError:
            proceed = messagebox.askyesno("Warning", "File already exists.\nOverwrite file?")
            if proceed:
                ww.save_world(world, self.file_name.get(), permission='w')
        except Exception as e:
            print(e)
            messagebox.showerror("Error", str(e))
        self.window.destroy()

    def palette_switch(self, palette):
        self.palette = palette
        self.refresh()

    def n_mode(self):
        self.palette_switch(nightdict)
        self.p_switch.config(text="Day mode", command=self.d_mode)

    def d_mode(self):
        self.palette_switch(colordict)
        self.p_switch.config(text="Night mode", command=self.n_mode)


def example_run():
    world_file = 'example_03.json'
    world = ww.load_world(world_file)

    root = tk.Tk()
    grid = Grid(world, master=root)
    grid.mainloop()

if __name__ == '__main__':
    example_run()