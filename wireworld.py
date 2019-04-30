


states = {0, 1, 2, 3}   # more generally, set(range(N))
relative_nbhd = ((-1,-1), (0,-1), (1,-1),
                 (-1, 0),         (1, 0),
                 (-1, 1), (0, 1), (1, 1))

def staterule(state, nbhd_state):
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
    def __init__(self, size=(7,7), content=None, staterule=staterule):
        self.staterule = staterule
        self.size = size
        keyset = {(x//size[0], x%size[1]) for x in range(size[0]*size[1])}     # create a set of coordinate tuples
        if content is None:
            self.grid = {k:0 for k in keyset}
        else:
            # TODO run checks on content, perhaps reformat
            self.grid = content


    def printself(self):
        # prints a representation of the current state in the console
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
        if value is None:
            state = self.grid.setdefault(coord, 0)
            state = (state-1) % (max(states)+1)
            self.grid[coord] = state


    def getneighbours(self, coord):
        state_dict = {state: 0 for state in states}
        for x,y in relative_nbhd:
            neighbour = (coord[0]+x, coord[1]+y)
            if neighbour in self.grid:
                state = self.grid[neighbour]
                state_dict[state] += 1
        return state_dict


    # maybe too verbose
    # def getcoordstate(self, coord):
    #     if coord in self.grid:
    #         return self.grid[coord]
    #     else:
    #         return 0


    def step(self):
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