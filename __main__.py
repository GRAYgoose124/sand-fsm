from functools import reduce
from itertools import islice
from machine import Rand, CharSub


def take(it, n):
    return list(islice(it, n))


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
