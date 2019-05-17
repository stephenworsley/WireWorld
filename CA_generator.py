from numpy.random import choice


def permuter(N):
    '''
    Generate all divisions of 8 into an N-tuple.

    This yields all N-tuples made up of positive integers such that the sum is 8.
    '''
    head_dict = {x: 8 for x in range(N)}
    head_dict[-1] = 0
    while True:
        pertmutation = tuple(head_dict[x]-head_dict[x-1] for x in range(N))
        yield pertmutation
        done = True
        for x in range(N-1):
            if head_dict[x] > 0:
                head_dict[x] -= 1
                for y in range(x):
                    head_dict[y] = head_dict[x]
                done = False
                break
        if done:
            break


def tup_to_dict(tup):
    '''Takes a tuple and returns a dictionary with the same values, whose keys are their indices.'''
    dictionary = {x: y for x, y in enumerate(tup)}
    return dictionary


def dict_to_tup(dictionary):
    '''Takes a dictionary whose keys are indices and returns their values as a tuple.'''
    tup = tuple(dictionary[x] for x in range(len(dictionary)))
    return tup


class CA_rules:
    '''Generates and stores CA rules in function and dictionary form.'''
    def __init__(self, CA_dict=None, N_states=3):
        if CA_dict is None:
            self.CA_dict = self.random_dict(N_states)
        else:
            self.CA_dict = CA_dict
        self.rules = self.make_rules(self.CA_dict)

    def random_dict(self, n_states, sparsity=0.6, conservatism=0.25):
        '''
        Generates a random dictionary describing the rules of a CA.

        Each key in the dictionary is a tuple of current cell state and the state of its neighbourhood, represented by
        a tuple whose contents at each index describes the number of neighbouring cells have the state associated with
        that index.
        sparsity and conservatism control the expected behaviour of the CA, note that sparsity and conservatism should
        not add to more than 1.

        Args:

        * n_states(int):
            describes the number of states of the CA

        Kwargs:

        * sparsity(float):
            a number between 0 and 1 which describes how often dead cells are created

        * conservatism(float):
            a number between 0 and 1 which describes how often cells retain their previous state.
        '''
        if sparsity < 0:
            raise Exception('sparsity should be greater than 0')
        if conservatism < 0:
            raise Exception('conservatism should be greater than 0')
        if sparsity + conservatism > 1:
            raise Exception('sparsity and conservatism should not add to more than 1')
        rule_dict = dict()
        for state in range(n_states):
            for permutation in permuter(n_states):
                key = (state, permutation)
                # the described CA will be 'semistable', dead cells far from live cells will remain dead.
                if permutation[0] == 8:
                    next_state = 0
                else:
                    # the distribution of next states is controlled to influence the behaviour of the CA.
                    def weight_rule(x):
                        if x == 0 and state == 0:
                            weight = 1 - (1-sparsity-conservatism) * (n_states - 1) / (n_states - 2)
                        elif x == 0:
                            weight = sparsity
                        elif x == state:
                            weight = conservatism
                        else:
                            weight = (1-sparsity-conservatism)/(n_states - 2)
                        return weight
                    weights = [weight_rule(x) for x in range(n_states)]
                    next_state = int(choice(list(range(n_states)), p=weights))
                rule_dict[key] = next_state
        return rule_dict

    def make_rules(self, CA_dict):
        '''
        Makes a function out of a dictionary describing the rules of a CA.

        Returned function is acceptable to the wireworld.CA class.
        '''
        def rules(state, nbhd_dict):
            nbhd_tup = dict_to_tup(nbhd_dict)
            key = (state, nbhd_tup)
            next_state = CA_dict[key]
            return next_state
        return rules


def testing():
    count = 0
    for x in permuter(3):
        print(x)
        count += 1

    print(count)
