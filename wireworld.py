# import tkinter as tk
import json
import CA_generator


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
    '''Contains the information needed to define a cellular automata'''
    def __init__(self, rule=None, mode=None, states=None, getrandom=False):
        if getrandom:
            if states is None:
                N = 3
            else:
                N = states
            ca_rules = CA_generator.CA_rules(N_states=N)
            self.rule = ca_rules.rules
            self.mode = 'semistable'
            self.states = set(range(N))
        else:
            self.rule = rule
            self.mode = mode
            if type(states) is int:
                self.states = set(range(states))
            else:
                self.states = states

ww_CA = CA(rule=ww_staterule, mode='stable', states=4)
life_CA = CA(rule=life_staterule, mode='semistable', states=2)
CA_dict = {'wireworld': ww_CA,
           'life': life_CA}

class World:
    '''
    An instance of a particular cellular automata or world.
    '''
    def __init__(self, size=(7,7), content=None, CA=None, CA_type='wireworld'): #, staterule = None, mode = None, states = None,

        '''
        Creates a particular cellular automata.

        Default cellular automata is wireworld.

        Args:

        * size (tuple):
            Sets the initial bounds of the world

        Kwargs:

        * content (dict):
            Sets the initial state of the cells
        * staterule (function):
            Sets the rules of the cellular automata
        * mode (string):
            Sets the behaviour of the implementation of the cellular automata rules.
            e.g. a mode of 'stable' will leave empty cells empty
        * states (set):
            The set of all possible states for a cell to be in.
        * CA_type (string):
            A label corresponding to the type of cellular automata to be run.
        '''
        # if mode is None:
        #     self.mode = CA_dict[CA_type].mode
        # else:
        #     self.mode = mode
        # if staterule is None:
        #     self.staterule = CA_dict[CA_type].rule
        # else:
        #     self.staterule = staterule
        # if states is None:
        #     self.states = CA_dict[CA_type].states
        # else:
        #     self.states = states
        self.CA_type = CA_type
        if CA is None:
            self.CA = CA_dict[CA_type]
        else:
            self.CA = CA
        self.size = size
        if content is None:
            keyset = {(x // size[0], x % size[1]) for x in
                      range(size[0] * size[1])}  # create a set of coordinate tuples
            self.grid = {k:0 for k in keyset}
        else:
            # TODO run checks on content, perhaps reformat
            self.grid = content


    def printself(self):
        '''prints a representation of the current state in the console'''
        for y in range(self.size[1]):
            rowlist = []
            for x in range(self.size[0]):
                try:
                    state = str(self.grid[(x,y)])
                except:
                    state = '*'
                rowlist.append(state)
            print('-'.join(rowlist))

    def editpoint(self, coord, value=None):
        '''
        Edit the state of a given cell.

        Default behaviour is to decrement the state, cycling from 0 to the max state.
        If a cell is empty, it is assumed to start at 0.

        Args:

            coord (tuple):
            2 dimensional coordinate describing the location of the cell.

        Kwargs:
            Value (int or None):
            sets the new state of the cell. If None, state is decremented

        '''
        if value is None:
            state = self.grid.setdefault(coord, 0)
            state = (state-1) % (max(self.CA.states)+1)
            self.grid[coord] = state


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
        for x,y in relative_nbhd:
            neighbour = (coord[0]+x, coord[1]+y)
            state = self.getcoordstate(neighbour)
            state_dict[state] += 1
            # if neighbour in self.grid:
            #     state = self.grid[neighbour]
            #     state_dict[state] += 1
        return state_dict


    def pad(self):
        '''Adds all cells adjacent to existing cells'''
        for coord in self.grid.copy():
            for x, y in relative_nbhd:
                neighbour = (coord[0] + x, coord[1] + y)
                self.grid.setdefault(neighbour, 0)

    def trim(self):
        '''Removes all cells containing zeroes'''
        for coord, state in self.grid.copy().items():
            if state == 0:
                del self.grid[coord]


    def getcoordstate(self, coord):
        if coord in self.grid:
            return self.grid[coord]
        else:
            return 0


    def step(self):
        '''Runs one step of the cellular automata.'''
        new_states = dict()
        if self.CA.mode == 'semistable':
            self.pad()
        for coord, state in self.grid.items():
            nbhd_state = self.getneighbours(coord)
            new_state = self.CA.rule(state, nbhd_state)
            new_states[coord] = new_state
        self.grid = new_states
        if self.CA.mode == 'stable' or self.CA.mode == 'semistable':
            self.trim()

    def getbounds(self):
        '''Returns the bounds for the position of the active cells.'''
        x_max = max(x for x,y in self.grid) # note: x,y is the coordinate, not the key value pair
        x_min = min(x for x,y in self.grid)
        y_max = max(y for x,y in self.grid)
        y_min = min(y for x,y in self.grid)
        return ((x_min,x_max), (y_min,y_max))

    def becomerandom(self, N=3):
        self.CA = CA(states=N, getrandom=True)
        self.CA_type = 'random'
        for coord, state in self.grid.items():
            self.grid[coord] = state % N


# this could be useful if i want to define rules from file
# def get_rules(rule_name):
#     '''Returns the appropriate staterule function.
#
#     Args:
#     * rule_name (string (or object))
#
#     Returns:
#         function
#     '''
#     state_rule = None
#     if rule_name == 'wire_world':
#         state_rule = ww_staterule
#     return state_rule

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
        state = {tuple(eval(k)): v for k,v in state.items()}
    elif type(state) is list:
        # TODO turn an array into a dict
        pass
    world = World(size=size, content=state, CA_type=CA_type)
    return world


def save_world(world, outfile, permission='x'):
    '''Saves World object as Json file.'''
    if outfile[-5:] != '.json':
        raise Exception('File name must end in .json')
    CA_type = world.CA_type
    size = world.size
    state = world.grid
    state = {str(k): v for k,v in state.items()}
    world_data = {'CA_type': CA_type,
                  'size': size,
                  'state': state}
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