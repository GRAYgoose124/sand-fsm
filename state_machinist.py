from abc import ABC, ABCMeta, abstractmethod
from typing import NamedTuple
from matplotlib import pyplot as plt
import networkx as nx


class GraphHistory(list):
    def __str__(self):
        return "GraphHistory[{}]".format(" -> ".join(self))


class PathResult(NamedTuple):
    success_tuple: tuple[bool, str | None]
    path_taken: GraphHistory

    @property
    def success(self):
        return self.success_tuple[0]

    @property
    def failure_state(self):
        return self.success_tuple[1]


class StateGraph(nx.DiGraph, metaclass=ABCMeta):
    START_STATE = "_S_"
    END_STATE = "_E_"

    def __init__(self, autobuild=True):
        super().__init__()
        self.add_node(StateGraph.START_STATE)
        self.add_node(StateGraph.END_STATE)

        self.history = GraphHistory()

        if autobuild:
            self.build()

        self.reset()

    @abstractmethod
    def build(self):
        pass

    def reset(self):
        self.history = GraphHistory([StateGraph.START_STATE])

    @property
    def actions(self):
        return self[self.current_state]

    @property
    def current_state(self):
        return self.history[-1]

    @property
    def done(self):
        return (
            self.current_state == StateGraph.END_STATE
        )  # or StateGraph.END_STATE in self.history

    def can_step(self, action):
        return action in self.actions

    def step(self, action, verbose=False):
        if verbose:
            print(
                f"{self.history}\nCan step from {self.current_state} to end: {self.can_step(StateGraph.END_STATE)}"
            )

        if self.done:
            return False

        if self.can_step(action):
            self.history.append(action)

            return True
        else:
            return False

    def take_path(self, path, reset=True):
        if self.done:
            if reset:
                self.reset()
            else:
                return PathResult((False, None), self.history)

        r = None
        for i, action in enumerate(path):
            if not self.step(action):
                r = PathResult((False, action), self.history)

        if r is None:
            r = PathResult((self.done, None), self.history)

        if reset:
            self.reset()

        return r


class MSG(StateGraph):
    def build(self):
        self.add_edges_from(
            [
                (StateGraph.START_STATE, "A"),
                ("A", "B"),
                ("A", "C"),
                ("A", "D"),
                ("B", "C"),
                ("B", "D"),
                ("C", "D"),
                ("C", "A"),
                ("D", StateGraph.END_STATE),
            ]
        )


def sparse_builder(G=MSG(), connectivity=0.5, nodes=10):
    for i in range(nodes):
        G.add_node(i)

    for i in range(nodes):
        for j in range(nodes):
            if i != j and (i + j) % (1 / connectivity) == 0:
                G.add_edge(i, j)

    return G


def basic_fsm_demo():
    fsm = MSG()

    path = ["A", "B", "C", "A", "D", StateGraph.END_STATE]
    result = fsm.take_path(path, reset=False)
    print(f"{result}\nHistory: {fsm.history} (Should match path_taken)")

    fsm.reset()
    fsm.take_path(result.path_taken)
    print(
        f"Post reset: (using the old path taken as input)\n{result}\nHistory: {fsm.history} (Should match path_taken)"
    )


def main():
    basic_fsm_demo()

    G = sparse_builder()
    nx.draw_networkx(G)
    plt.show()


if __name__ == "__main__":
    main()
