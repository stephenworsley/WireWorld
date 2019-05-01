# import tkinter
import json


states = {0, 1, 2, 3}   # more generally, set(range(N))
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


class CA:
    '''Contains the information needed to define a cellular automata'''
    def __init__(self, rule, mode, states):
        self.rule = rule
        self.mode = mode
        if type(states) is int:
            self.states = set(range(states))
        else:
            self.states = states

ww_CA = CA(rule=ww_staterule, mode='stable', states=4)
CA_dict = {'wireworld': ww_CA}

class World:
    '''
    An instance of a particular cellular automata or world.
    '''
    def __init__(self, size=(7,7), content=None, staterule=None, mode=None, states=None, CA_type='wireworld'):
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
        '''
        if mode is None:
            self.mode = CA_dict[CA_type].mode
        else:
            self.mode = mode
        if staterule is None:
            self.staterule = CA_dict[CA_type].rule
        else:
            self.staterule = staterule
        if states is None:
            self.states = CA_dict[CA_type].states
        else:
            self.states = states
        self.CA_type = CA_type
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
            state = (state-1) % (max(self.states)+1)
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
        state_dict = {state: 0 for state in self.states}
        for x,y in relative_nbhd:
            neighbour = (coord[0]+x, coord[1]+y)
            if neighbour in self.grid:
                state = self.grid[neighbour]
                state_dict[state] += 1
        return state_dict


    def pad(self):
        '''Adds all cells adjacent to existing cells'''
        # TODO decide what to do when adding cells outside the border
        for coord in self.grid:
            for x, y in relative_nbhd:
                neighbour = (coord[0] + x, coord[1] + y)
                self.grid.setdefault(neighbour, 0)

    def trim(self):
        '''Removes all cells containing zeroes'''
        for coord, state in self.grid.items():
            if state == 0:
                del(coord)


    # may be a useful method if I rethink implementation
    # def getcoordstate(self, coord):
    #     if coord in self.grid:
    #         return self.grid[coord]
    #     else:
    #         return 0


    def step(self):
        '''Runs one step of the cellular automata.'''
        new_states = dict()
        if self.mode == 'semistable':
            self.pad()
        for coord, state in self.grid.items():
            nbhd_state = self.getneighbours(coord)
            new_state = self.staterule(state, nbhd_state)
            new_states[coord] = new_state
        self.grid = new_states
        if self.mode == 'stable' or self.mode == 'semistable':
            self.trim()


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


def load_world(infile):
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


def save_world(world, outfile):
    CA_type = world.CA_type
    size = world.size
    state = world.grid
    state = {str(k): v for k,v in state.items()}
    world_data = {'CA_type': CA_type,
                  'size': size,
                  'state': state}
    with open(outfile, 'w') as json_file:
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

example_run()