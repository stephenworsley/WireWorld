import copy
import tkinter as tk
from tkinter import messagebox
import wireworld as ww


# set the palettes to be used
# TODO generate dictionaries for an arbitrary number of states, perhaps with matplotlib colormaps
colordict = {0: 'white', 1: 'red', 2: 'blue', 3: 'yellow'}
nightdict = {0: 'black', 1: 'red', 2: 'blue', 3: 'yellow'}
oob_color = 'red'


class Grid(tk.Frame):
    '''The frame containing the wireworld GUI.'''
    def __init__(self, world, master=None, size=None):
        '''
        Generate all the main tkinter widgets.

        Args

        * world(wireworld.World object):
            The cellular automata instance which the widgets will interact with.

        Kwargs:

        * master(tkinter object):
            The parent of the Grid.
        * size(tuple):
            Describes the size of the initial display.
        '''
        super().__init__(master)
        self.pack()  # place self inside master

        # pack the sub-frames
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(side='top')
        self.controls = tk.Frame(self)
        self.controls.pack(side='bottom')
        self.labels = tk.Frame(self.controls)
        self.labels.pack(side='bottom', fill='x')
        self.copy_paste_frame = tk.Frame(self)
        self.copy_paste_frame.pack(side='right')
        self.d_pad = tk.Frame(self)
        self.d_pad.pack(side='top')

        # set flags to default values
        self.zoomed = False
        self.copy_stage = None
        self.paste_stage = None
        self.erase_stage = None
        self.first_coord = None
        self.second_coord = None

        if size is None:
            self.size = world.size
        else:
            self.size = size
        # set default North West offset value
        self.grid_NW = (0, 0)
        self.world = world

        self.palette = colordict

        # create size change buttons
        self.grb_na = tk.Button(self.grid_frame, text='+')
        self.grb_ea = tk.Button(self.grid_frame, text='+')
        self.grb_wa = tk.Button(self.grid_frame, text='+')
        self.grb_sa = tk.Button(self.grid_frame, text='+')
        self.grb_nd = tk.Button(self.grid_frame, text='-')
        self.grb_ed = tk.Button(self.grid_frame, text='-')
        self.grb_wd = tk.Button(self.grid_frame, text='-')
        self.grb_sd = tk.Button(self.grid_frame, text='-')
        # save default button color
        self.default_color_bg = self.grb_na.cget('background')
        self.default_color_abg = self.grb_na.cget('activebackground')

        # create and grid the button display and size change buttons
        self.display_world()

        # set the size change button commands
        self.add_n = self.grid_arrow_factory(orientation='N', operation='+')
        self.add_e = self.grid_arrow_factory(orientation='E', operation='+')
        self.add_w = self.grid_arrow_factory(orientation='W', operation='+')
        self.add_s = self.grid_arrow_factory(orientation='S', operation='+')
        self.del_n = self.grid_arrow_factory(orientation='N', operation='-')
        self.del_e = self.grid_arrow_factory(orientation='E', operation='-')
        self.del_w = self.grid_arrow_factory(orientation='W', operation='-')
        self.del_s = self.grid_arrow_factory(orientation='S', operation='-')
        self.grb_na.config(command=self.add_n)
        self.grb_ea.config(command=self.add_e)
        self.grb_wa.config(command=self.add_w)
        self.grb_sa.config(command=self.add_s)
        self.grb_nd.config(command=self.del_n)
        self.grb_ed.config(command=self.del_e)
        self.grb_wd.config(command=self.del_w)
        self.grb_sd.config(command=self.del_s)

        # fill the main control panel
        self.update_button = tk.Button(self.controls, text='Update', command=self.w_update)
        self.update_button.pack(side='left')
        self.run_button = tk.Button(self.controls, text='Run', command=self.click_run, width=5)
        self.run_button.pack(side='left')
        self.running = False  # this is set to True as long as the CA is running.

        self.checkpoint_button = tk.Button(self.controls, text='Checkpoint', command=self.checkpoint)
        self.checkpoint_button.pack(side='left')
        self.reset_button = tk.Button(self.controls, text='Reset', command=self.reset)
        self.reset_button.pack(side='left')
        self.cache = None #  this will contain a copy of the world when the checkpoint button was last pressed
        self.clear_button = tk.Button(self.controls, text='Clear', command=self.clear)
        self.clear_button.pack(side='left')

        self.file_button = tk.Button(self.controls, text='Load/Save', command=self.open_file_window)
        self.file_button.pack(side='right')
        self.p_switch = tk.Button(self.controls, text='Night mode', command=self.n_mode)
        self.p_switch.pack(side='right')
        self.random_button = tk.Button(self.controls, text='Become random', command=self.becomerandom)
        self.random_button.pack(side='right')
        self.zoom_button = tk.Button(self.controls, text='Zoom out', command=self.zoom_out)
        self.zoom_button.pack(side='right')

        # fill the labels in the control panel
        self.delay = tk.IntVar()
        self.delay.set(500)
        self.delay_entry = tk.Entry(self.labels, textvariable=self.delay, width=6)
        self.delay_label = tk.Label(self.labels, text='Delay')
        self.delay_label.pack(side='left')
        self.delay_entry.pack(side='left')
        self.livecellcount = tk.Label(self.labels, text='Number of live cells: ')
        self.livecellcount.pack(side='left')
        self.spansize = tk.Label(self.labels, text='Horizontal span:  Vertical span: ')
        self.spansize.pack(side='left')
        self.cellcountupdate()
        self.stepcount = tk.IntVar(0)
        self.steps = tk.Label(self.labels, text='steps: {}'.format(self.stepcount.get()))
        self.steps.pack(side='right')
        self.stepcount.trace('w', self.stepchange)
        self.stepcache = 0

        # fill the copy paste button frame
        self.copy_button = tk.Button(self.copy_paste_frame, text='Copy', command=self.begin_copy)
        self.copy_button.grid(row=0, column=0)
        self.paste_button = tk.Button(self.copy_paste_frame, text='Paste', command=self.begin_paste)
        self.paste_button.grid(row=0, column=1)
        self.erase_button = tk.Button(self.copy_paste_frame, text='Erase', command=self.begin_erase)
        self.erase_button.grid(row=0, column=2)
        self.confirm_button = tk.Button(self.copy_paste_frame, text='Confirm', command=self.confirm)
        self.confirm_button.grid(row=1, column=2)
        self.stop_button = tk.Button(self.copy_paste_frame, text='Stop', command=self.stop_copy_paste)
        self.stop_button.grid(row=1, column=0)
        self.mode_label = tk.Label(self.copy_paste_frame, text='Current mode: Edit')
        self.mode_label.grid(row=2, column=0, columnspan=3)

        # fill the movement frame
        self.movement = tk.IntVar()  # this will control how many steps will be moved
        self.movement.set(1)
        self.movement_entry = tk.Entry(self.d_pad, textvariable=self.movement, width=3)
        self.movement_entry.grid(row=1, column=1)
        self.d_N = tk.Button(self.d_pad, text='N')
        self.d_N.grid(row=0, column=1)
        self.d_E = tk.Button(self.d_pad, text='E')
        self.d_E.grid(row=1, column=2, sticky='W')
        self.d_W = tk.Button(self.d_pad, text='W')
        self.d_W.grid(row=1, column=0)
        self.d_S = tk.Button(self.d_pad, text='S')
        self.d_S.grid(row=2, column=1)
        self.zoom_locked = tk.IntVar()
        self.zoom_lock = tk.Checkbutton(self.d_pad, text='Zoom lock', variable=self.zoom_locked,
                                        onvalue=1, offvalue=0)
        self.zoom_lock.grid(row=2, column=2, columnspan=2)

        # set commands for the move buttons
        self.move_N = self.move_factory('N')
        self.move_E = self.move_factory('E')
        self.move_W = self.move_factory('W')
        self.move_S = self.move_factory('S')
        self.d_N.config(command=self.move_N)
        self.d_E.config(command=self.move_E)
        self.d_W.config(command=self.move_W)
        self.d_S.config(command=self.move_S)

    def coord_map(self, coord, backwards=False):
        '''Maps from a coordinate on the button array to a coordinate on the world.'''
        if self.zoomed:
            nw = self.zoomed_NW
        else:
            nw = self.grid_NW
        if backwards:
            new_coord = (coord[0]-nw[0], coord[1]-nw[1])
        else:
            new_coord = (coord[0]+nw[0], coord[1]+nw[1])
        return new_coord

    def display_world(self):
        '''Initialises buttons based on world data.'''
        self.button_array = []
        for y in range(self.size[1]):
            row = []
            for x in range(self.size[0]):
                w_coord = self.coord_map((x, y))
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

        if self.zoomed:
            self.zc.grid(row=2, column=2, rowspan=self.size[1], columnspan=self.size[0])

    def indicate_oob(self):
        '''Changes the color of the grid arrow buttons to indicate the presence of live cells out of bounds.'''
        if self.zoomed:
            size = self.zoomed_size
            nw = self.zoomed_NW
        else:
            size = self.size
            nw = self.grid_NW
        xb_min, yb_min = nw
        xb_max = xb_min + size[0] - 1
        yb_max = yb_min + size[1] - 1
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
        self.spansize.config(text='Horizontal span: {} Vertical span: {}'.format(width, height))

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
            if self.copy_stage == 1:
                self.first_copy(w_coord)
            elif self.copy_stage == 2 or self.copy_stage == 3:
                self.second_copy(w_coord)
            elif self.paste_stage == 1 or self.paste_stage == 2:
                self.first_paste(w_coord)
            elif self.erase_stage == 1:
                self.first_erase(w_coord)
            elif self.erase_stage == 2 or self.erase_stage == 3:
                self.second_erase(w_coord)
            else:
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
                self.button_array[y][x].config(command=self.command_generator((x, y)))

    def refresh(self, full=True):
        '''Sets all the appropriate colors to the button grid.'''
        if full or self.world.CA.mode != 'stable':  # wireworld shouldn't add or remove live cells while self updating
            self.indicate_oob()
            self.cellcountupdate()

        if self.zoomed:
            size = self.zoomed_size
        else:
            size = self.size

        # We loop through the minimal number of cells in order to refresh,
        # either all the displayed cells or all the changed cells.
        if full or len(self.world.changeset) > size[0]*size[1]:
            for y in range(size[1]):
                for x in range(size[0]):
                    w_coord = self.coord_map((x, y))
                    if full or w_coord in self.world.changeset:
                        color = self.getcolor(w_coord)
                        self.update_color(color, (x, y))
        else:
            for coord in self.world.changeset:
                w_coord = coord
                x, y = self.coord_map(coord, backwards=True)
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

    def grid_arrow_factory(self, orientation, operation):
        '''Returns a function which will change the size of the display in the appropriate direction.'''
        def mover():
            # set the amount by which to add or subtract
            if self.zoomed:
                span = 14
            else:
                span = 1

            # change the size of the displayed area
            if operation == '+':
                delta = 1
            elif operation == '-':
                if (orientation == 'E' or orientation == 'W') and self.size[0] <= 1:
                    return
                if (orientation == 'N' or orientation == 'S') and self.size[1] <= 1:
                    return
                delta = -1
            if orientation == 'N' or orientation == 'S':
                self.size = (self.size[0], self.size[1] + delta)
                if self.zoomed:
                    self.zoomed_size = (self.zoomed_size[0], self.zoomed_size[1] + delta*span)
                if orientation == 'N':
                    self.grid_NW = (self.grid_NW[0], self.grid_NW[1] - delta)
                    if self.zoomed:
                        self.zoomed_NW = (self.zoomed_NW[0], self.zoomed_NW[1] - delta*span)
            elif orientation == 'E' or orientation == 'W':
                self.size = (self.size[0] + delta, self.size[1])
                if self.zoomed:
                    self.zoomed_size = (self.zoomed_size[0] + delta*span, self.zoomed_size[1])
                if orientation == 'W':
                    self.grid_NW = (self.grid_NW[0] - delta, self.grid_NW[1])
                    if self.zoomed:
                        self.zoomed_NW = (self.zoomed_NW[0] - delta*span, self.zoomed_NW[1])
            if self.zoomed:
                # expand the canvas
                self.zc.config(width=self.zoomed_size[0]*2, height=self.zoomed_size[1]*2)
                size = self.zoomed_size
            else:
                size = self.size

            # add or remove rows or columns
            if operation == '+':
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
                            w_coord = self.coord_map((x, y))
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
                                display_row.insert(0, x)
            if operation == '-':
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

            if self.zoomed:
                self.zc.box_grid(self)
            else:
                self.set_button_commands()
                self.grid_buttons()
            self.grid_arrows()
            self.indicate_oob()
            if self.paste_stage == 2 and operation == '+':
                self.preview_paste(self.first_coord)
        return mover

    def move_factory(self, orientation):
        '''Return a function which moves the display window.'''
        def move():
            zoom_locked = self.zoom_locked.get()
            try:
                movement = self.movement.get()
            except:
                return
            if self.zoomed and zoom_locked == 1:
                    move_dict = {'N': (0, -1), 'E': (1, 0),
                                 'W': (-1, 0), 'S': (0, 1)}
                    move_vector = move_dict[orientation]
                    self.grid_NW = (self.grid_NW[0] + move_vector[0]*movement,
                                    self.grid_NW[1] + move_vector[1]*movement)
                    self.zc.box_grid(self)
            else:
                adder, remover = self.get_arrows(orientation)
                if type(movement) is not int:
                    return
                for x in range(movement):
                    adder()
                    remover()
        return move

    def get_arrows(self, orientation):
        '''Returns a pair of functions which describe how to move in a given direction.'''
        if orientation == 'N':
            adder = self.add_n
            remover = self.del_s
        elif orientation == 'E':
            adder = self.add_e
            remover = self.del_w
        elif orientation == 'W':
            adder = self.add_w
            remover = self.del_e
        elif orientation == 'S':
            adder = self.add_s
            remover = self.del_n
        else:
            raise Exception('Bad orientation')
        return adder, remover

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
        '''Replaces the button array with a zoomed out canvas.'''
        self.stop_copy_paste()
        self.zoomed_NW = (self.grid_NW[0] - self.size[0] * 7, self.grid_NW[1] - self.size[1] * 7)
        self.zc = ZoomedCanvas(master=self.grid_frame, grid=self)
        self.zoom_button.config(text='Zoom in', command=self.zoom_in)
        self.zc.grid(row=2, column=2, rowspan=self.size[1], columnspan=self.size[0])
        self.destroy_buttons()
        self.zoomed_size = (self.zc.width, self.zc.height)
        self.zoomed = True
        self.refresh()

    def zoom_in(self):
        '''Replaces the canvas with a zoomed in button array.'''
        self.zc.destroy()
        self.zoom_button.config(text='Zoom out', command=self.zoom_out)
        self.zoomed = False
        self.display_world()
        self.refresh()

    def is_in_grid(self, coord):
        '''Checks if a coordinate is within the bounds of the button_array.'''
        if coord is None:
            return False
        if coord[0] < 0 or coord[1] < 0 or coord[0] >= self.size[0] or coord[1] >= self.size[1]:
            return False
        else:
            return True

    def reset_stage(self):
        '''Resets copy/paste state to default.'''
        if self.paste_stage == 2:
            self.refresh()
        first_w = self.first_coord
        second_w = self.second_coord
        if first_w is not None:
            last_coord = self.coord_map(first_w, backwards=True)
            if self.is_in_grid(last_coord):
                lx, ly = last_coord
                self.button_array[ly][lx].config(bitmap='')
        if second_w is not None:
            last_coord = self.coord_map(second_w, backwards=True)
            if self.is_in_grid(last_coord):
                lx, ly = last_coord
                self.button_array[ly][lx].config(bitmap='')
        self.copy_stage = None
        self.paste_stage = None
        self.erase_stage = None

    def stop_copy_paste(self):
        '''Exits copy/paste mode.'''
        self.reset_stage()
        self.mode_label.config(text='Current mode: Edit')

    def begin_copy(self):
        '''Begins the process of copying.'''
        self.reset_stage()
        self.copy_stage = 1
        self.mode_label.config(text='Current mode: Copy')

    def begin_paste(self):
        '''Begins the process of pasting.'''
        self.reset_stage()
        self.paste_stage = 1
        self.mode_label.config(text='Current mode: Paste')

    def begin_erase(self):
        '''Begins the process of erasing.'''
        self.reset_stage()
        self.erase_stage = 1
        self.mode_label.config(text='Current mode: Erase')

    def confirm(self):
        '''Completes the process of copy/pasting.'''
        action = self.get_action()
        action()

    def get_action(self):
        '''Returns the appropriate copy/paste function to be called.'''
        if self.copy_stage == 3:
            action = self.copy_action
        elif self.paste_stage == 2:
            action = self.paste_action
        elif self.erase_stage == 3:
            action = self.erase_action
        else:
            action = lambda: None
        return action

    def copy_action(self):
        '''Saves a copy of the states within a specified area.'''
        self.world.save_copy(self.first_coord, self.second_coord)
        self.stop_copy_paste()

    def paste_action(self):
        '''Copies the saved states to the specified location.'''
        self.world.paste_copy(self.first_coord)
        self.stop_copy_paste()
        self.refresh()
        self.world_bounds = self.world.getbounds()
        self.indicate_oob()

    def erase_action(self):
        '''Sets cell states to 0 or None within specified area.'''
        self.world.erase_section(self.first_coord, self.second_coord)
        self.stop_copy_paste()
        self.refresh()
        self.world_bounds = self.world.getbounds()
        self.indicate_oob()

    def first_copy(self, w_coord):  # TODO make the button size uniform somehow, or maybe it's a feature
        '''Sets the first coordinate after the copy process has started.'''
        last_w_coord = self.first_coord
        if last_w_coord is not None:
            last_coord = self.coord_map(last_w_coord, backwards=True)
            if self.is_in_grid(last_coord):
                lx, ly = last_coord
                self.button_array[ly][lx].config(bitmap='')
        self.first_coord = w_coord
        coord = self.coord_map(w_coord, backwards=True)
        x, y = coord
        self.button_array[y][x].config(bitmap='gray75', fg='green')
        self.copy_stage = 2

    def second_copy(self, w_coord):
        '''Sets the second coordinate after the copy process has started.'''
        last_w_coord = self.second_coord
        if last_w_coord is not None:
            last_coord = self.coord_map(last_w_coord, backwards=True)
            if self.is_in_grid(last_coord):
                lx, ly = last_coord
                if last_w_coord == self.first_coord:
                    self.button_array[ly][lx].config(bitmap='gray75')
                else:
                    self.button_array[ly][lx].config(bitmap='')
        self.second_coord = w_coord
        coord = self.coord_map(w_coord, backwards=True)
        x, y = coord
        self.button_array[y][x].config(bitmap='gray25', fg='green')
        self.copy_stage = 3

    def first_paste(self, w_coord):
        '''
        Sets the first coordinate after the paste process has started.

        Also shows a preview of the result.
        '''
        if self.paste_stage == 2:
            self.refresh()
        last_w_coord = self.first_coord
        if last_w_coord is not None:
            last_coord = self.coord_map(last_w_coord, backwards=True)
            if self.is_in_grid(last_coord):
                lx, ly = last_coord
                self.button_array[ly][lx].config(bitmap='')
        self.first_coord = w_coord
        coord = self.coord_map(w_coord, backwards=True)
        x, y = coord
        self.button_array[y][x].config(bitmap='gray75', fg='green')
        self.paste_stage = 2
        self.preview_paste(coord)

    def preview_paste(self, origin_coord):
        '''Shows a preview of the result of confirming the paste action.'''
        if self.world.copy_section is not None:
            top_left = (origin_coord[0] + self.world.copy_section.offset[0],
                        origin_coord[1] + self.world.copy_section.offset[1])
            for dy, row in enumerate(self.world.copy_section.state_array):
                for dx, state in enumerate(row):
                    coord = (top_left[0] + dx, top_left[1] + dy)
                    if self.is_in_grid(coord):
                        if state is None:
                            display_state = 0
                        else:
                            display_state = state
                        color = self.palette[display_state]
                        x, y = coord
                        self.button_array[y][x].config(bg=color, activebackground=color)

    def first_erase(self, w_coord):
        '''Sets the first coordinate after the erase process has started.'''
        last_w_coord = self.first_coord
        if last_w_coord is not None:
            last_coord = self.coord_map(last_w_coord, backwards=True)
            if self.is_in_grid(last_coord):
                lx, ly = last_coord
                self.button_array[ly][lx].config(bitmap='')
        self.first_coord = w_coord
        coord = self.coord_map(w_coord, backwards=True)
        x, y = coord
        self.button_array[y][x].config(bitmap='gray75', fg='green')
        self.erase_stage = 2

    def second_erase(self, w_coord):
        '''Sets the second coordinate after the erase process has started.'''
        last_w_coord = self.second_coord
        if last_w_coord is not None:
            last_coord = self.coord_map(last_w_coord, backwards=True)
            if self.is_in_grid(last_coord):
                lx, ly = last_coord
                if last_w_coord == self.first_coord:
                    self.button_array[ly][lx].config(bitmap='gray75')
                else:
                    self.button_array[ly][lx].config(bitmap='')
        self.second_coord = w_coord
        coord = self.coord_map(w_coord, backwards=True)
        x, y = coord
        self.button_array[y][x].config(bitmap='gray25', fg='green')
        self.erase_stage = 3


class ZoomedCanvas(tk.Canvas):
    '''A canvas containing a zoomed out view of the CA.'''
    def __init__(self, master=None, width=None, height=None, grid=None):
        if grid is None:
            self.width = width
            self.height = height
        else:
            self.width = grid.size[0]*14
            self.height = grid.size[1]*14
        self.pix_size = 2  # set the size of the pixels/cells
        super().__init__(master, width=self.width * self.pix_size, height=self.height * self.pix_size)

        self.setpixels()
        self.o_box = None
        self.box_grid(grid)

    def setpixels(self):
        '''fill the canvas with pixels to be edited later.'''
        self.pixel_array = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                rec = self.create_rectangle(x*self.pix_size, y*self.pix_size,
                                            x*self.pix_size + 1, y*self.pix_size + 1)
                row.append(rec)
            self.pixel_array.append(row)

    def setoriginbox(self, big_NW, small_NW, small_size):
        '''Creates a box at the given coordinates.'''
        x0 = (small_NW[0]-big_NW[0])*self.pix_size - 1
        y0 = (small_NW[1]-big_NW[1])*self.pix_size - 1
        x1 = x0 + (small_size[0]*self.pix_size) + 1
        y1 = y0 + (small_size[1]*self.pix_size) + 1
        if self.o_box is None:
            self.o_box = self.create_rectangle(x0, y0, x1, y1,
                                               fill='', outline='gray', outlinestipple='gray50', tags='o_box')
        else:
            self.coords('o_box', x0, y0, x1, y1)
            self.lift('o_box')

    def box_grid(self, grid):
        '''Sets the box to be around the zoomed in part.'''
        self.setoriginbox(grid.zoomed_NW, grid.grid_NW, grid.size)


    def changepix(self, coord, color):
        '''Sets the color of a pixel at a given coordinate.'''
        x, y = coord
        pix_ID = self.pixel_array[y][x]
        self.itemconfig(pix_ID, outline=color)


def example_run():
    '''Launches the GUI with an example file.'''
    world_file = 'example_06.json'
    world = ww.load_world(world_file)

    root = tk.Tk()
    grid = Grid(world, master=root)
    grid.mainloop()


if __name__ == '__main__':
    example_run()
