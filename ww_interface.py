import wireworld as ww
import tkinter as tk


# TODO generate dictionaries for an arbitrary number of states, perhaps with matplotlib colormaps
colordict = {0: 'white', 1: 'red', 2: 'blue', 3: 'yellow'}


class Grid(tk.Frame):
    '''Generates the wireworld GUI.'''
    def __init__(self, world, master=None, size=None):
        super().__init__(master)
        self.grid()
        self.world = world
        if size is None:
            self.size = world.size
        else:
            self.size = size
        self.button_array = []
        for x in range(self.size[0]):
            row = []
            for y in range(self.size[1]):
                color = self.getcolor((x,y))
                button = tk.Button(self, relief="raised", bg=color, command=self.command_generator((x,y)))
                button.grid(row=x, column=y)
                row.append(button)
            self.button_array.append(row)
        self.update = tk.Button(self, text='Update', command=self.update)
        self.update.grid(row=self.size[0], columnspan=3, sticky='W')

    def getcolor(self, coord):
        '''Returns the color associated with the specified state.'''
        state = self.world.getcoordstate(coord)
        color = colordict[state]
        return color

    def command_generator(self, coord):
        '''Generates a command to update the button in the specified position.'''
        def command():
            self.world.editpoint(coord)
            color = self.getcolor(coord)
            x,y = coord
            self.button_array[x][y].config(bg=color)
        return command

    def update(self):
        '''Updates the cellular automata.'''
        self.world.step()
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                color = self.getcolor((x,y))
                self.button_array[x][y].config(bg=color)


def example_run():
    world_file = 'example_01.json'
    world = ww.load_world(world_file)

    root = tk.Tk()
    grid = Grid(world, master=root)
    grid.mainloop()

if __name__ == '__main__':
    example_run()