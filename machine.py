from collections.abc import Iterator
import random

from itertools import islice


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class Machine(Iterator):
    def __init__(self):
        self.state = None
        self.rules = []

    def __next__(self):
        raise NotImplementedError


class Rand(Machine):
    def __next__(self):
        return self.rules[random.randint(0, len(self.rules)-1)]


class Substitution(Machine):
    def __next__(self):
        new_state = ""
        for c in self.state:
            for currp, nextp in self.rules:
                if c == currp:
                    new_state += nextp
                    break

            self.state = new_state
        return self.state
