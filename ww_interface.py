import wireworld as ww
import tkinter as tk
from tkinter import  messagebox
import copy


# set the palettes to be used
# TODO generate dictionaries for an arbitrary number of states, perhaps with matplotlib colormaps
colordict = {0: 'white', 1: 'red', 2: 'blue', 3: 'yellow'}
nightdict = {0: 'black', 1: 'red', 2: 'blue', 3: 'yellow'}
oob_color = 'red'


class Grid(tk.Frame):
    '''Generates the wireworld GUI.'''
    def __init__(self, world, master=None, size=None):
        super().__init__(master)
        self.pack()
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(side= 'top')
        self.zoomed = False

        self.palette = colordict
        if size is None:
            self.size = world.size
        else:
            self.size = size
        self.grid_NE = (0,0)
        self.world = world


        self.grb_na = tk.Button(self.grid_frame, text='+', command=self.add_n)
        self.grb_ea = tk.Button(self.grid_frame, text='+')
        self.grb_wa = tk.Button(self.grid_frame, text='+', command=self.add_w)
        self.grb_sa = tk.Button(self.grid_frame, text='+', command=self.add_s)
        self.grb_nd = tk.Button(self.grid_frame, text='-', command=self.del_n)
        self.grb_ed = tk.Button(self.grid_frame, text='-', command=self.del_e)
        self.grb_wd = tk.Button(self.grid_frame, text='-', command=self.del_w)
        self.grb_sd = tk.Button(self.grid_frame, text='-', command=self.del_s)
        self.default_color_bg = self.grb_na.cget('background')
        self.default_color_abg = self.grb_na.cget('activebackground')


        self.display_world()

        self.update_button = tk.Button(self, text='Update', command=self.w_update)
        self.update_button.pack(side = 'left')
        self.run_button = tk.Button(self, text='Run', command=self.click_run, width=5)
        self.run_button.pack(side = 'left')
        self.running = False

        self.checkpoint_button = tk.Button(self, text='Checkpoint', command=self.checkpoint)
        self.checkpoint_button.pack(side='left')
        self.reset_button = tk.Button(self, text= 'Reset', command=self.reset)
        self.reset_button.pack(side='left')
        self.cache = None
        self.clear_button = tk.Button(self, text='Clear', command=self.clear)
        self.clear_button.pack(side='left')
        self.delay = tk.IntVar()
        self.delay.set(500)
        self.delay_entry = tk.Entry(textvariable=self.delay, width=6)
        self.delay_label = tk.Label(text='Delay')
        self.delay_label.pack(side='left')
        self.delay_entry.pack(side='left')
        self.livecellcount = tk.Label(text='Number of live cells: ')
        self.livecellcount.pack(side='left')
        self.spansize = tk.Label(text='Horizontal span:  Vertical span: ')
        self.spansize.pack(side='left')
        self.cellcountupdate()
        self.stepcount = tk.IntVar(0)
        self.steps = tk.Label(text='steps: {}'.format(self.stepcount.get()))
        self.steps.pack(side='right')
        self.stepcount.trace('w', self.stepchange)
        self.stepcache = 0

        self.file_button = tk.Button(self, text='Load/Save', command=self.open_file_window)
        self.file_button.pack(side='right')
        self.p_switch = tk.Button(self, text='Night mode', command=self.n_mode)
        self.p_switch.pack(side='right')
        self.random_button = tk.Button(self, text='Become random', command=self.becomerandom)
        self.random_button.pack(side='right')
        self.zoom_button = tk.Button(self, text='Zoom out', command=self.zoom_out)
        self.zoom_button.pack(side='right')

        self.add_e = self.grid_arrow_factory(orientation='E', function='+')
        self.grb_ea.config(command=self.add_e)

    def coord_map(self, coord, reversed=False):
        '''Maps from a coordinate on the button array to a coordinate on the world.'''
        if self.zoomed:
            NW = self.zoomed_NW
        else:
            NW = self.grid_NE
        if reversed:
            new_coord = (coord[0]-NW[0], coord[1]-NW[1])
        else:
            new_coord = (coord[0]+NW[0], coord[1]+NW[1])
        return new_coord

    def display_world(self):
        '''Initialises buttons based on world data.'''
        self.button_array = []
        for y in range(self.size[1]):
            row = []
            for x in range(self.size[0]):
                w_coord = self.coord_map((x,y))
                color = self.getcolor(w_coord)
                button = tk.Button(self.grid_frame, relief="raised", bg=color,
                                   activebackground=color)
                row.append(button)
            self.button_array.append(row)
        self.set_button_commands()
        self.grid_buttons()
        self.grid_arrows()
        self.world_bounds = self.world.getbounds()
        self.indicate_oob()

    def grid_buttons(self):
        '''Places the buttons representing the cellular automata.'''
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.button_array[y][x].grid(row=y+2, column=x+2)

    def grid_arrows(self):
        '''Positions the "grid arrow" buttons appropriately for the size of the grid.'''
        self.grb_na.config(width=self.size[0]*4 - 4)
        self.grb_nd.config(width=self.size[0]*4 - 4)
        self.grb_sd.config(width=self.size[0]*4 - 4)
        self.grb_sa.config(width=self.size[0]*4 - 4)
        self.grb_wa.config(height=self.size[1]*2 - 1)
        self.grb_wd.config(height=self.size[1]*2 - 1)
        self.grb_ed.config(height=self.size[1]*2 - 1)
        self.grb_ea.config(height=self.size[1]*2 - 1)

        self.grb_na.grid(row=0, column=2, columnspan=self.size[0])
        self.grb_nd.grid(row=1, column=2, columnspan=self.size[0])
        self.grb_sd.grid(row=self.size[1]+2, column=2, columnspan=self.size[0])
        self.grb_sa.grid(row=self.size[1]+3, column=2, columnspan=self.size[0])
        self.grb_wa.grid(row=2, column=0, rowspan=self.size[1])
        self.grb_wd.grid(row=2, column=1, rowspan=self.size[1])
        self.grb_ed.grid(row=2, column=self.size[0]+2, rowspan=self.size[1])
        self.grb_ea.grid(row=2, column=self.size[0]+3, rowspan=self.size[1])

    def indicate_oob(self):
        '''Changes the color of the grid arrow buttons to indicate the presence of live cells out of bounds.'''
        if self.zoomed:
            size = self.zoomed_size
            NW = self.zoomed_NW
        else:
            size = self.size
            NW = self.grid_NE
        xb_min, yb_min = NW
        xb_max = xb_min + size[0] -1
        yb_max = yb_min + size[1] -1
        if self.world_bounds is None:
            x_range = (xb_min, xb_max)
            y_range = (yb_min, yb_max)
        else:
            x_range, y_range = self.world_bounds
        if xb_min > x_range[0]:
            self.grb_wa.config(bg=oob_color, activebackground=oob_color)
        else:
            self.grb_wa.config(bg=self.default_color_bg, activebackground=self.default_color_abg)
        if yb_min > y_range[0]:
            self.grb_na.config(bg=oob_color, activebackground=oob_color)
        else:
            self.grb_na.config(bg=self.default_color_bg, activebackground=self.default_color_abg)
        if xb_max < x_range[1]:
            self.grb_ea.config(bg=oob_color, activebackground=oob_color)
        else:
            self.grb_ea.config(bg=self.default_color_bg, activebackground=self.default_color_abg)
        if yb_max < y_range[1]:
            self.grb_sa.config(bg=oob_color, activebackground=oob_color)
        else:
            self.grb_sa.config(bg=self.default_color_bg, activebackground=self.default_color_abg)

    def cellcountupdate(self):
        '''Displays the current number of cells and the space they take up.'''
        self.livecellcount.config(text='Number of live cells: ' + str(self.world.livecellcount()))
        if self.world_bounds is None:
            width = 0
            height = 0
        else:
            width = self.world_bounds[0][1] - self.world_bounds[0][0]
            height = self.world_bounds[1][1] - self.world_bounds[1][0]
        self.spansize.config(text='Horizontal span: {} Vertical span: {}'.format(width,height))

    def getcolor(self, coord):
        '''Returns the color associated with the specified state.'''
        state = self.world.getcoordstate(coord)
        color = self.palette[state]
        return color

    def command_generator(self, coord):
        '''Generates a command to update the button in the specified position.'''
        x, y = coord
        button = self.button_array[y][x]
        def command():
            w_coord = self.coord_map(coord)
            self.world.editpoint(w_coord)
            color = self.getcolor(w_coord)
            button.config(bg=color, activebackground=color)
            self.world_bounds = self.world.getbounds()
            self.cellcountupdate()
            self.stepcount.set(0)
        return command

    def set_button_commands(self):
        '''Assigns the buttons in the grid with the appropriate commands'''
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.button_array[y][x].config(command=self.command_generator((x,y)))

    # This seems to be one of the bottlenecks for speed, this could be improved by keeping track of which buttons
    # are necessary to update.
    def refresh(self, full=True):
        '''Sets all the appropriate colors to the button grid.'''
        if full or self.world.CA.mode != 'stable': # wireworld should never add or remove live cells while self updating
            self.indicate_oob()
            self.cellcountupdate()

        if self.zoomed:
            size = self.zoomed_size
            NW = self.zoomed_NW
        else:
            size = self.size
            NW = self.grid_NE

        # We loop through the minimal number of cells in order to refresh,
        # either all the displayed cells or all the changed cells.
        if full or len(self.world.changeset) > size[0]*size[1]: # TODO size reformat
            for y in range(size[1]):
                for x in range(size[0]):
                    w_coord = self.coord_map((x,y))
                    if full or w_coord in self.world.changeset:
                        color = self.getcolor(w_coord)
                        self.update_color(color, (x,y))
        else:
            for coord in self.world.changeset:
                w_coord = coord
                x, y = self.coord_map(coord, reversed=True)
                if x >= 0 and x < size[0] and y >= 0 and y < size[1]:
                    color = self.getcolor(w_coord)
                    self.update_color(color, (x, y))


    def update_color(self, color, coord):
        '''Updates the color of the cell at the chosen coordinate for the current display.'''
        x, y = coord
        if self.zoomed:
            self.zc.changepix(coord, color)
        else:
            self.button_array[y][x].config(bg=color, activebackground=color)

    def stepchange(self, *args):
        '''This is called and updates the steps label whenever self.stepcount changes.'''
        self.steps.config(text='steps: {}'.format(self.stepcount.get()))

    def w_update(self):
        '''Updates the cellular automata.'''
        self.world.step()
        self.world_bounds = self.world.getbounds()
        self.refresh(full=False)
        self.stepcount.set(self.stepcount.get() + 1)

    def click_run(self):
        '''Starts the run loop.'''
        self.run_button.config(text='Pause', command=self.pause)
        self.run()

    def run(self):
        '''The main body of the run loop. Updates and tries to call itself again if conditions are met.'''
        self.running = True
        self.w_update()
        try:
            delay = self.delay.get()
        except:
            delay = None
        if delay == 0 or type(delay) is not int:
            self.pause()
        else:
            self.after(self.delay.get(), self.runcheck)

    def runcheck(self):
        '''Recursively calls the run function unless the app has been paused.'''
        if self.running:
            self.run()

    def pause(self):
        '''Stops the run loop.'''
        self.run_button.config(text='Run', command=self.click_run)
        self.running = False

    def checkpoint(self):
        '''Creates a copy of current world data.'''
        self.cache = copy.deepcopy(self.world)
        self.stepcache = self.stepcount.get()

    def reset(self):
        '''Loads world data from the cache and pauses.'''
        if self.cache is None:
            return
        self.pause()
        self.world = copy.deepcopy(self.cache)
        self.world_bounds = self.world.getbounds()
        self.refresh()
        self.stepcount.set(self.stepcache)

    def clear(self):
        '''Removes world grid data and pauses.'''
        self.pause()
        self.world.grid = dict()
        self.world_bounds = None
        self.refresh()
        self.stepcount.set(0)

    def open_file_window(self):
        '''Opens a window with load and save options.'''
        self.pause()
        if self.zoomed:
            self.zoom_in()
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

    def destroy_buttons(self):
        '''Destroys all the buttons in the button array.'''
        for y in self.button_array:
            for x in y:
                x.destroy()
        self.button_array = []


    def load(self):
        '''Attempts to load and display world data from file.'''
        try:
            world = ww.load_world(self.file_name.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self.destroy_buttons()
        self.world = world
        self.size = self.world.size
        self.display_world()
        self.window.destroy()
        self.stepcount.set(0)

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

    def grid_arrow_factory(self, orientation, function):
        def mover():
            # set the amount by which to add or subtract
            if self.zoomed:
                span = 14
            else:
                span = 1

            if function == '+':
                delta = 1
            elif function == '-':
                if (orientation == 'E' or orientation == 'W') and self.size[0] <= 1: # TODO size change
                    return
                if (orientation == 'N' or orientation == 'S') and self.size[1] <= 1:
                    return
                delta = -1
            if orientation == 'N' or orientation == 'S':
                self.size = (self.size[0], self.size[1] + delta)
                if self.zoomed:
                    self.zoomed_size = (self.zoomed_size[0], self.zoomed_size[1] + delta*span)
                if orientation == 'N':
                    self.grid_NE = (self.grid_NE[0],self.grid_NE[1] - delta)
            elif orientation == 'E' or orientation == 'W':
                self.size = (self.size[0] + delta, self.size[1])
                if self.zoomed:
                    self.zoomed_size = (self.zoomed_size[0] + delta*span, self.zoomed_size[1])
                if orientation == 'W':
                    self.grid_NE = (self.grid_NE[0] - delta, self.grid_NE[1])

            if self.zoomed:
                # expand the canvas
                self.zc.config(width=self.zoomed_size[0]*2, height=self.zoomed_size[1]*2)
                size = self.zoomed_size
            else:
                size = self.size
            if function == '+':
                if orientation == 'N' or orientation == 'S':
                    if self.zoomed and orientation == 'N':
                        self.zc.move('all', 0, span*self.zc.pix_size)
                    rows = []
                    for dy in range(span):
                        row = []
                        if orientation == 'N':
                            y = dy
                        else:
                            y = dy + size[1] - span
                        for x in range(size[0]):
                            w_coord = self.coord_map((x,y))
                            color = self.getcolor(w_coord)
                            if self.zoomed:
                                display_object = self.zc.create_rectangle(x*self.zc.pix_size, y*self.zc.pix_size,
                                                                          x*self.zc.pix_size+1, y*self.zc.pix_size+1,
                                                                          outline=color)
                            else:
                                display_object = tk.Button(self.grid_frame, relief="raised", bg=color,
                                                           activebackground=color)
                            row.append(display_object)
                        rows.append(row)
                    if self.zoomed:
                        display_array = self.zc.pixel_array
                    else:
                        display_array = self.button_array
                    if orientation == 'N':
                        for row in reversed(rows):
                            display_array.insert(0, row)
                    elif orientation == 'S':
                        for row in rows:
                            display_array.append(row)
                if orientation == 'E' or orientation == 'W':
                    if self.zoomed and orientation == 'W':
                        self.zc.move('all', span*self.zc.pix_size, 0)

                    rows = []
                    for y in range(size[1]):
                        row = []
                        for dx in range(span):
                            if orientation == 'E':
                                x = dx + size[0] - span
                            elif orientation == 'W':
                                x = dx
                            w_coord = self.coord_map((x,y))
                            color = self.getcolor(w_coord)
                            if self.zoomed:
                                display_object = self.zc.create_rectangle(x*self.zc.pix_size, y*self.zc.pix_size,
                                                                          x*self.zc.pix_size+1, y*self.zc.pix_size+1,
                                                                          outline=color)
                            else:
                                display_object = tk.Button(self.grid_frame, relief="raised", bg=color,
                                                           activebackground=color)
                            row.append(display_object)
                        rows.append(row)
                    if self.zoomed:
                        display_array = self.zc.pixel_array
                    else:
                        display_array = self.button_array
                    if orientation == 'E':
                        for display_row, extra_row in zip(display_array, rows):
                            display_row.extend(extra_row)
                    elif orientation == 'W':
                        for display_row, extra_row in zip(display_array, rows):
                            for x in reversed(extra_row):
                                display_row.insert(0,x)

            if function == '-':
                if self.zoomed:
                    display_object = self.zc.pixel_array
                else:
                    display_object = self.button_array
                if orientation == 'N' or orientation == 'S':
                    if orientation == 'N':
                        pop_side = 0
                    else:
                        pop_side = -1
                    for y in range(span):
                        row = display_object.pop(pop_side)
                        for cell in row:
                            if self.zoomed:
                                self.zc.delete(cell)
                            else:
                                cell.destroy()
                if orientation == 'E' or orientation == 'W':
                    if orientation == 'W':
                        pop_side = 0
                    else:
                        pop_side = -1
                    for row in display_object:
                        for x in range(span):
                            cell = row.pop(pop_side)
                            if self.zoomed:
                                self.zc.delete(cell)
                            else:
                                cell.destroy()
                if self.zoomed and orientation == 'N':
                    self.zc.move('all', 0, -span*self.zc.pix_size)
                if self.zoomed and orientation == 'W':
                    self.zc.move('all', -span*self.zc.pix_size, 0)

            if not self.zoomed:
                self.set_button_commands()
                self.grid_buttons()
            self.grid_arrows()
            self.indicate_oob()
        return mover
    #
    # self.add_e = grid_arrow_factory(orientation='E', function='+')








    def add_n(self):
        self.grid_NE = (self.grid_NE[0],self.grid_NE[1]-1)
        self.size = (self.size[0],self.size[1]+1)
        button_row =[]
        y = 0
        for x in range(self.size[0]):
            w_coord = self.coord_map((x,y))
            color = self.getcolor(w_coord)
            button = tk.Button(self.grid_frame, relief="raised", bg=color,
                               activebackground=color)
            button_row.append(button)
        self.button_array.insert(0, button_row)
        self.set_button_commands()
        self.grid_buttons()
        self.grid_arrows()
        self.indicate_oob()

        # This code also works and is more concise but affects performance slightly.
        # self.grid_NE = (self.grid_NE[0],self.grid_NE[1]-1)
        # self.size = (self.size[0],self.size[1]+1)
        # for y in self.button_array:
        #     for x in y:
        #         x.destroy()
        # self.display_world()

    # def add_e(self):
    #     self.size = (self.size[0]+1, self.size[1])
    #     x = self.size[0]-1
    #     for y, button_row in enumerate(self.button_array):
    #         w_coord = self.coord_map((x,y))
    #         color = self.getcolor(w_coord)
    #         button = tk.Button(self.grid_frame, relief="raised", bg=color,
    #                            activebackground=color)
    #         button_row.append(button)
    #     self.set_button_commands()
    #     self.grid_buttons()
    #     self.grid_arrows()
    #     self.indicate_oob()

    def add_w(self):
        self.grid_NE = (self.grid_NE[0]-1, self.grid_NE[1])
        self.size = (self.size[0]+1, self.size[1])
        x = 0
        for y, button_row in enumerate(self.button_array):
            w_coord = self.coord_map((x,y))
            color = self.getcolor(w_coord)
            button = tk.Button(self.grid_frame, relief="raised", bg=color,
                               activebackground=color)
            button_row.insert(0, button)
        self.set_button_commands()
        self.grid_buttons()
        self.grid_arrows()
        self.indicate_oob()

    def add_s(self):
        self.size = (self.size[0], self.size[1]+1)
        button_row =[]
        y = self.size[1]-1
        for x in range(self.size[0]):
            w_coord = self.coord_map((x,y))
            color = self.getcolor(w_coord)
            button = tk.Button(self.grid_frame, relief="raised", bg=color,
                               activebackground=color)
            button_row.append(button)
        self.button_array.append(button_row)
        self.set_button_commands()
        self.grid_buttons()
        self.grid_arrows()
        self.indicate_oob()

    def del_n(self):
        if self.size[1] <= 1:
            return
        self.grid_NE = (self.grid_NE[0], self.grid_NE[1]+1)
        self.size = (self.size[0],self.size[1]-1)
        button_row = self.button_array[0]
        for x in button_row:
            x.destroy()
        self.button_array.pop(0)
        self.set_button_commands()
        self.grid_arrows()
        self.grid_buttons()
        self.indicate_oob()

    def del_e(self):
        if self.size[0] <= 1:
            return
        self.size = (self.size[0]-1, self.size[1])
        for button_row in self.button_array:
            button = button_row[-1]
            button.destroy()
            button_row.pop(-1)
        self.set_button_commands()
        self.grid_arrows()
        self.grid_buttons()
        self.indicate_oob()

    def del_w(self):
        if self.size[0] <= 1:
            return
        self.grid_NE = (self.grid_NE[0]+1, self.grid_NE[1])
        self.size = (self.size[0]-1, self.size[1])
        for button_row in self.button_array:
            button = button_row[0]
            button.destroy()
            button_row.pop(0)
        self.set_button_commands()
        self.grid_arrows()
        self.grid_buttons()
        self.indicate_oob()

    def del_s(self):
        if self.size[1] <= 1:
            return
        self.size = (self.size[0],self.size[1]-1)
        button_row = self.button_array[-1]
        for x in button_row:
            x.destroy()
        self.button_array.pop(-1)
        self.set_button_commands()
        self.grid_arrows()
        self.grid_buttons()
        self.indicate_oob()

    def palette_switch(self, palette):
        '''
        Changes the colors assigned to each state.

        Args:
        * pallette (dict)
            A dictionary from states to their colors.
        '''
        self.palette = palette
        self.refresh()

    def n_mode(self):
        '''Change the colors to a darker palette, toggle the button.'''
        self.palette_switch(nightdict)
        self.p_switch.config(text="Day mode", command=self.d_mode)

    def d_mode(self):
        '''Change the colors to a lighter palette, toggle the button.'''
        self.palette_switch(colordict)
        self.p_switch.config(text="Night mode", command=self.n_mode)

    def becomerandom(self):
        '''Changes current cellular automata rule for a randomly generated one.'''
        self.world.becomerandom(4)
        self.refresh()

    def zoom_out(self):

        self.zc = ZoomedCanvas(master=self.grid_frame, grid=self) # TODO cached size becomes size, add zoomed size
        # self.cached_NE = self.grid_NE
        # self.cached_size = self.size
        self.zoom_button.config(text='Zoom in', command=self.zoom_in)
        self.zc.grid(row=2, column=2, rowspan=self.size[1], columnspan=self.size[0])
        self.destroy_buttons()
        self.zoomed_NW = self.zc.NW
        self.zoomed_size = (self.zc.width, self.zc.height)
        self.zoomed = True
        self.refresh()

    def zoom_in(self):
        self.zc.destroy()
        self.zoom_button.config(text='Zoom out', command=self.zoom_out)
        # self.grid_NE = self.cached_NE
        # self.size = self.cached_size
        self.zoomed = False
        self.display_world()
        self.refresh()




class ZoomedCanvas(tk.Canvas):
    def __init__(self, master=None, NW=None, width=None, height=None, grid=None):
        if grid is None:
            self.NW = NW
            self.width = width
            self.height = height
        else:
            self.NW = (grid.grid_NE[0] - grid.size[0] * 7, grid.grid_NE[1] - grid.size[1] * 7)
            self.width = grid.size[0]*14
            self.height = grid.size[1]*14
        self.pix_size = 2 # set the size of the pixekls/cells
        super().__init__(master, width=self.width * self.pix_size, height=self.height * self.pix_size)

        self.setpixels()
        self.setoriginbox(self.NW, grid.grid_NE, grid.size)

    def setpixels(self):
        self.pixel_array = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                rec = self.create_rectangle(x*self.pix_size, y*self.pix_size,
                                            x*self.pix_size + 1, y*self.pix_size + 1)
                row.append(rec)
            self.pixel_array.append(row)

    def setoriginbox(self, big_NE, small_NE, small_size):
        x0 = (small_NE[0]-big_NE[0])*self.pix_size - 1
        y0 = (small_NE[1]-big_NE[1])*self.pix_size - 1
        x1 = x0 + (small_size[0]*self.pix_size) + 1
        y1 = y0 + (small_size[1]*self.pix_size) + 1
        self.create_rectangle(x0, y0, x1, y1,
                              fill='', outline='gray', outlinestipple='gray50', tags='o_box')

    def changepix(self, coord, color):
        x, y = coord
        pix_ID = self.pixel_array[y][x]
        self.itemconfig(pix_ID, outline=color)



def example_run():
    world_file = 'example_06.json'
    world = ww.load_world(world_file)

    root = tk.Tk()
    grid = Grid(world, master=root)
    grid.mainloop()

if __name__ == '__main__':
    example_run()