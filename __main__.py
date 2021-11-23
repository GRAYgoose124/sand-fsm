from functools import reduce

from machine import Rand, Substitution


def take(It, n):
    for _ in range(n):
        yield next(It)


class DNA(Rand):
    def __init__(self):
        self.state = ""
        self.rules = ["A", "G", "T", "C"]

    # def __next__(self):
    #     self.state += super().__next__()
    #     return self.state


class DNA2MRNA(Substitution):
    def __init__(self, initial_state):
        self.state = initial_state
        self.rules = [("G", "C"),
                      ("C", "G"),
                      ("T", "A"),
                      ("A", "U")]


class Walk(Rand):
    def __init__(self):
        self.rules = [1, -1]


if __name__ == '__main__':
    # print(reduce(lambda x, y: x+y, take(Walk(), 10)))

    a = "".join(list(take(DNA(), 10)))
    print(a)

    b = DNA2MRNA(a)
    print(next(b))
