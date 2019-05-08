import random

def permuter(N):
    '''Generate all divisions of 8 into an N-tuple'''
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
    dictionary = {x: y for x, y in enumerate(tup)}
    return dictionary

def dict_to_tup(dictionary):
    tup = tuple(dictionary[x] for x in range(len(dictionary)))
    return tup


# for simplicity, I may restrict myself here to CAs with 3 states
class CA_rules:
    def __init__(self, CA_dict=None, N_states=3):
        if CA_dict is None:
            self.CA_dict = self.random_dict(N_states)
        else:
            self.CA_dict = CA_dict
        self.rules = self.make_rules(self.CA_dict)

    def random_dict(self, N):
        rule_dict = dict()
        for state in range(N):
            for permutation in permuter(N):
                key = (state,permutation)
                if permutation[0] == 8:
                    next_state = 0
                else:
                    next_state = random.randint(0,N-1)
                rule_dict[key] = next_state
        return rule_dict

    def make_rules(self, CA_dict):
        def rules(state, nbhd_dict):
            nbhd_tup = dict_to_tup(nbhd_dict)
            key = (state, nbhd_tup)
            next_state = CA_dict[key]
            return next_state
        return rules


# iterator = iter(permuter(3))
def testing():
    count = 0
    for x in permuter(3):
        print(x)
        count +=1

    print(count)

