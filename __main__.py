import itertools
import functools
import random
from collections.abc import Iterator


class Machine(Iterator):
    def __init__(self):
        self.state = None
        self.rules = []

    def __next__(self):
        raise NotImplementedError


class RandMachine(Machine):
    def __next__(self):
        for next_state, probability in self.rules:
            if random.uniform(0, 1) > probability:
                self.state += next_state
                break

        return self.state


class DNA(RandMachine):
    def __init__(self, initial_state):
        self.state = initial_state
        self.rules = [("A", 0.25),
                      ("G", 0.25),
                      ("T", 0.25),
                      ("C", 0.25)]


class Walk(RandMachine):
    def __init__(self, initial_state):
        self.state = initial_state
        self.rules = [(1, 0.5),
                      (-1, 0.5)]


if __name__ == '__main__':
    walker = Walk(0)
    for step in walker:
        print(step)
