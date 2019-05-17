import json
import CA_generator


# defines the relative points that a cell considers its neighbours
relative_nbhd = ((-1,-1), (0,-1), (1,-1),
                 (-1, 0),         (1, 0),
                 (-1, 1), (0, 1), (1, 1))


def ww_staterule(state, nbhd_state):
    '''
    The rules for the wireworld cellular automata.

    Returns the next state for a given cell.

    Args:

    * state (int):
        The state of the current cell.
    * nbhd_state (dict)
        A dictionary whose keys are the possible states and whose values are the number of adjacent
        cells which have those states.
    Returns:
        int
    '''
    next_state = 0
    if state == 1:
        next_state = 2
    if state == 2:
        next_state = 3
    if state == 3:
        if nbhd_state[1] == 1 or nbhd_state[1] == 2:
            next_state = 1
        else:
            next_state = 3
    return next_state


def life_staterule(state, nbhd_state):
    '''Rules for John Conway's game of life.'''
    next_state = 0
    if state == 0:
        if nbhd_state[1] == 3:
            next_state = 1
    if state == 1:
        if nbhd_state[1] == 2 or nbhd_state[1] == 3:
            next_state = 1
    return next_state


class CA:
    '''Contains the information needed to define a cellular automata.'''
    def __init__(self, rule=None, mode=None, states=None, getrandom=False, ruledict=None):
        '''
        Generate the information necessary to generate a cellular automata (CA).

        Kwargs

        * rule(function):
            The function to be called when deciding the next state.
        * mode(string):
            Describes how to handle dead cells for performance.
        * states(int or set):
            Describes the possible states the CA can be in.
            If states is a set, it is expected to be of the form set(range(n))
        * getrandom(bool):
            If true, generates a random CA.
        * ruledict(dict):
            May be passed in place of rule. A rule will be constructed from ruledict.
        '''
        if getrandom:
            if states is None:
                n = 3
            elif type(states) is int:
                n = states
            else:
                n = len(states)
            # Initialise a
            ca_rules = CA_generator.CA_rules(N_states=n)
            self.rule = ca_rules.rules
            self.mode = 'semistable'
            self.states = set(range(n))
            self.ruledict = ca_rules.CA_dict

        elif ruledict is not None:
            self.ruledict = ruledict
            ca_rules = CA_generator.CA_rules(CA_dict=ruledict)
            self.rule = ca_rules.rules
            self.mode = mode
            if type(states) is int:
                self.states = set(range(states))
            else:
                self.states = states
        else:
            self.rule = rule
            self.mode = mode
            if type(states) is int:
                self.states = set(range(states))
            else:
                self.states = states
            self.ruledict = None


# initialise the relevant CA objects and store them in a dictionary for reference
ww_CA = CA(rule=ww_staterule, mode='stable', states=4)
life_CA = CA(rule=life_staterule, mode='semistable', states=2)
CA_dict = {'wireworld': ww_CA,
           'life': life_CA}


class World:
    '''
    An instance of a particular cellular automata or world.
    '''
    def __init__(self, size=(7, 7), content=None, CA=None, CA_type='wireworld'):

        '''
        Creates a particular cellular automata.

        Default cellular automata is wireworld.

        Args:

        * size (tuple):
            Sets the initial bounds of the world

        Kwargs:

        * content (dict):
            Sets the initial state of the cells
        * CA(CA object):
            Contains the information about the cellular automata to be run.
        * CA_type (string):
            A label corresponding to the type of cellular automata to be run.
            May be passed in place of CA.
        '''
        self.CA_type = CA_type
        if CA is None:
            self.CA = CA_dict[CA_type]
        else:
            self.CA = CA
        self.size = size
        if content is None:
            self.grid = dict()
        else:
            # TODO run checks on content, perhaps reformat
            self.grid = content
        self.changeset = set(self.grid)  # This set keeps track of which cells have changed after each update
        self.copy_section = None  # This keeps track of copied sections

    def printself(self):
        '''prints a representation of the current state in the console.'''
        for y in range(self.size[1]):
            rowlist = []
            for x in range(self.size[0]):
                try:
                    state = str(self.grid[(x, y)])
                except:
                    state = '*'
                rowlist.append(state)
            print('-'.join(rowlist))

    def editpoint(self, coord, value=None, cycle=True):
        '''
        Edit the state of a given cell.

        Default behaviour is to decrement the state, cycling from 0 to the max state.
        If a cell is empty, it is assumed to start at 0.

        Args:

        * coord (tuple):
            2 dimensional coordinate describing the location of the cell.

        Kwargs:
        * value (int or None):
            sets the new state of the cell. If None, state is decremented
        '''
        if value is None:
            if cycle:
                state = self.grid.setdefault(coord, 0)
                state = (state-1) % (max(self.CA.states)+1)
            else:
                state = 0
        else:
            state = value
            state = state % (max(self.CA.states)+1)  # force the resulting state to be valid
        if state == 0 and (self.CA.mode == 'stable' or self.CA.mode == 'semistable') and coord in self.grid:
            self.grid.pop(coord)
        else:
            self.grid[coord] = state
        self.changeset = set(coord)

    def getneighbours(self, coord):
        '''
        Returns the states of neighbouring cells.

        Args:

        * coord (tuple):
            2 dimensional coordinate describing the location of the cell.

        Returns:
            dict
        '''
        state_dict = {state: 0 for state in self.CA.states}
        for x, y in relative_nbhd:
            neighbour = (coord[0]+x, coord[1]+y)
            state = self.getcoordstate(neighbour)
            state_dict[state] += 1
        return state_dict

    def pad(self):
        '''Adds all cells adjacent to existing cells.'''
        for coord in self.grid.copy():
            for x, y in relative_nbhd:
                neighbour = (coord[0] + x, coord[1] + y)
                self.grid.setdefault(neighbour, 0)

    def trim(self):
        '''Removes all cells containing zeroes.'''
        for coord, state in self.grid.copy().items():
            if state == 0 or (self.CA_type == 'random' and (max(coord) > 120 or min(coord) < -120)):
                del self.grid[coord]

    def getcoordstate(self, coord):
        '''
        Returns the state at a coordinate, with empty coordinates defaulting to 0.

        Returns:
            int
        '''
        if coord in self.grid:
            return self.grid[coord]
        else:
            return 0

    def step(self):
        '''Runs one step of the cellular automata.'''
        new_states = dict()
        if self.CA.mode == 'semistable':
            self.pad()
        self.changeset = set()
        for coord, state in self.grid.items():
            nbhd_state = self.getneighbours(coord)
            new_state = self.CA.rule(state, nbhd_state)
            new_states[coord] = new_state
            if state != new_state:
                self.changeset.add(coord)
        self.grid = new_states
        if self.CA.mode == 'stable' or self.CA.mode == 'semistable':
            self.trim()

    def getbounds(self):
        '''Returns the bounds for the position of the active cells.'''
        if not bool(self.grid):
            return None
        x_max = max(x for x, y in self.grid)  # note: x,y is the coordinate, not the key value pair
        x_min = min(x for x, y in self.grid)
        y_max = max(y for x, y in self.grid)
        y_min = min(y for x, y in self.grid)
        return (x_min, x_max), (y_min, y_max)

    def livecellcount(self):
        '''Returns the number of live cells.'''
        return len(self.grid)

    def becomerandom(self, N=3):
        '''Exchange current CA with a randomly generated one.'''
        self.CA = CA(states=N, getrandom=True)
        self.CA_type = 'random'
        for coord, state in self.grid.items():
            self.grid[coord] = state % N

    def save_copy(self, first_coord, second_coord):
        '''Save the data within the selected region'''
        self.copy_section = CopySection(self, first_coord, second_coord)

    def paste_copy(self, origin):
        '''Paste the copied section from the selected point'''
        if self.copy_section is not None:
            top_left = (origin[0] + self.copy_section.offset[0], origin[1] + self.copy_section.offset[1])
            for dy, row in enumerate(self.copy_section.state_array):
                for dx, state in enumerate(row):
                    coord = (top_left[0] + dx, top_left[1] + dy)
                    self.editpoint(coord, value=state, cycle=False)

    def erase_section(self, first_coord, second_coord):
        '''Erase all points within the chosen section'''
        top_left = (min(first_coord[0], second_coord[0]), min(first_coord[1], second_coord[1]))
        bottom_right = (max(first_coord[0], second_coord[0]), max(first_coord[1], second_coord[1]))
        for x in range(top_left[0], bottom_right[0] + 1):
            for y in range(top_left[1], bottom_right[1] + 1):
                coord = (x, y)
                if self.CA.mode == 'stable' or self.CA.mode == 'semistable':
                    if coord in self.grid:
                        del self.grid[coord]
                else:
                    self.grid[coord] = 0


class CopySection:
    '''Keeps track of copied sections'''
    def __init__(self, world, first_coord, second_coord):
        '''Create a copy of the world coordinates between the specified coordinates.'''
        self.state_array = self.calculate_state_array(world, first_coord, second_coord)
        self.offset = self.calculate_offset(first_coord, second_coord)
        self.max_states = self.calculate_max_states()

    def calculate_state_array(self, world, first_coord, second_coord):
        '''Returns an array containing all the states within the specified coordinates.'''
        coord_array = self.calculate_coord_array(first_coord, second_coord)
        state_array = []
        for coord_row in coord_array:
            state_row = []
            for coord in coord_row:
                if coord in world.grid:
                    state = world.grid[coord]
                else:
                    state = None
                state_row.append(state)
            state_array.append(state_row)
        return state_array

    def calculate_coord_array(self, first_coord, second_coord):
        '''Returns an array containing all the coordinates within the specified coordinates.'''
        top_left = (min(first_coord[0], second_coord[0]), min(first_coord[1], second_coord[1]))
        bottom_right = (max(first_coord[0], second_coord[0]), max(first_coord[1], second_coord[1]))
        array = [[(x, y) for x in range(top_left[0], bottom_right[0]+1)] for y in range(top_left[1], bottom_right[1]+1)]
        return array

    def calculate_offset(self, first_coord, second_coord):
        '''Returns the difference between the top left coord of the state_array and the first specified coord.'''
        top_left = (min(first_coord[0], second_coord[0]), min(first_coord[1], second_coord[1]))
        offset = (top_left[0] - first_coord[0], top_left[1] - first_coord[1])
        return offset

    def calculate_max_states(self):
        '''
        Keeps track of the maximum stored state.

        Thsi may be useful if pasting to a different CA.
        '''
        def none_to_zero(row):
            return [0 if x is None else x for x in row]
        max_state = max([max(none_to_zero(row)) for row in self.state_array])
        return max_state


#TODO add these as mothods for World
def load_world(infile):
    '''Loads Json file into a World object.'''
    if infile[-5:] != '.json':
        raise Exception('File name must end in .json')
    with open(infile) as json_file:
        world_data = json.load(json_file)
    CA_type = world_data['CA_type']
    size = tuple(world_data['size'])
    state = world_data['state']
    if type(state) is dict:
        state = {tuple(eval(k)): v for k, v in state.items()}
    elif type(state) is list:
        # TODO turn an array into a dict
        pass
    if 'ruledict' in world_data:
        string_ruledict = world_data['ruledict']
        ruledict = {eval(k): v for k, v in string_ruledict.items()}
        n_states = world_data['Nstates']
        mode = world_data['mode']
        ca = CA(mode=mode, states=n_states, ruledict=ruledict)
        world = World(size=size, content=state, CA=ca, CA_type=CA_type)
    else:
        world = World(size=size, content=state, CA_type=CA_type)
    return world


def save_world(world, outfile, permission='x'):
    '''Saves World object as Json file.'''
    if outfile[-5:] != '.json':
        raise Exception('File name must end in .json')
    CA_type = world.CA_type
    size = world.size
    state = world.grid
    state = {str(k): v for k, v in state.items()}
    ruledict = world.CA.ruledict
    world_data = {'CA_type': CA_type,
                  'size': size,
                  'state': state}
    if ruledict is not None:
        string_dict = {str(k): v for k, v in ruledict.items()}
        world_data['ruledict'] = string_dict
        world_data['Nstates'] = len(world.CA.states)
        world_data['mode'] = world.CA.mode
    with open(outfile, permission) as json_file:
        json.dump(world_data, json_file)


def example_run():
    # test_dict = {(0,1): 3, (1,0): 3, (1,2): 1, (2,1): 2}
    #
    # world = World(content=test_dict)
    infile = 'example_01.json'
    outfile = 'example_out_01.json'
    world = load_world(infile)
    world. printself()
    print('---')
    world.step()
    world.printself()
    print('---')
    world.editpoint((1,3))
    world.step()
    world.printself()
    save_world(world, outfile)

    infile_2 = 'example_02.json'
    world = load_world(infile_2)
    print('---')
    print('---')
    world.printself()
    for _ in range(4):
        print('---')
        world.step()
        world.printself()

    save_world(world, infile_2, permission='x')


if __name__ == "__main__":
    example_run()
