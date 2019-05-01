# import tkinter


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


class World:
    '''
    An instance of a particular cellular automata or world.
    '''
    def __init__(self, size=(7,7), content=None, staterule=ww_staterule, mode='stable'):
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
        self.mode = mode
        self.staterule = staterule
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
                # state = str(self.grid.setdefault((x,y), '*'))
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
            state = (state-1) % (max(states)+1)
            self.grid[coord] = state


    def getneighbours(self, coord):
        '''
        Returns the states of neighbouring cells.

        Depending on self.mode, this will also create neighbouring cells

        Args:

        * coord (tuple):
            2 dimensional coordinate describing the location of the cell.

        Returns:
            dict
        '''
        mode = self.mode
        state_dict = {state: 0 for state in states}
        if mode == 'semistable' and self.grid[coord] == 0:
            mode = 'stable'
        for x,y in relative_nbhd:
            neighbour = (coord[0]+x, coord[1]+y)
            if mode == 'stable':
                if neighbour in self.grid:
                    state = self.grid[neighbour]
                    state_dict[state] += 1
            if mode == 'semistable':
                state = self.grid.setdefault(neighbour, 0)
                state_dict[state] += 1
        return state_dict


    # may be a useful method if I rethink implementation
    # def getcoordstate(self, coord):
    #     if coord in self.grid:
    #         return self.grid[coord]
    #     else:
    #         return 0


    def step(self):
        '''Runs one step of the cellular automata.'''
        new_states = dict()
        for coord, state in self.grid.items():
            nbhd_state = self.getneighbours(coord)
            new_state = self.staterule(state, nbhd_state)
            new_states[coord] = new_state
        self.grid = new_states

def example_run():
    test_dict = {(0,1): 3, (1,0): 3, (1,2): 1, (2,1): 2}

    world = World(content=test_dict)
    world. printself()
    print('---')
    world.step()
    world.printself()
    print('---')
    world.editpoint((1,3))
    world.step()
    world.printself()

example_run()