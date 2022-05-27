from collections.abc import Iterator
from random import randint

def take(it, n):
    return list(islice(it, n))


class Machine(Iterator):
    def __init__(self, s=None, rules=None):
        self.state = s
        self.rules = rules

    def __next__(self):
        raise NotImplementedError


class Rand(Machine):
    def __next__(self):
        return self.rules[randint(0, len(self.rules)-1)]


class CharSub(Machine):
    def __next__(self):
        new_state = ""
        for c in self.state:
            for cp, np in self.rules:
                if c == cp:
                    new_state += np
                    break

            self.state = new_state
        return self.state


class StrSub(Machine):
    def __next__(self):
        pass


if __name__ == '__main__':
    walk = reduce(lambda x, y: x+y, take(Rand(0, [1, -1]), 1000))
    print(walk)

    dna = "".join(take(Rand("", ["A", "T", "G", "C"]), 10))
    print(dna)

    mrna = next(CharSub(dna, [("G", "C"),
                              ("C", "G"),
                              ("T", "A"),
                              ("A", "U")]))

    print(mrna)
