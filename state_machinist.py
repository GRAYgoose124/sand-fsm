from abc import ABC, abstractmethod
from typing import NamedTuple
import networkx


class GraphHistory(list):
    def __str__(self):
        return " -> ".join(self)


class PathResult(NamedTuple):
    success_tuple: tuple[bool, str | None]
    path: GraphHistory

    @property
    def success(self):
        return self.success_tuple[0]

    @property
    def failure_state(self):
        return self.success_tuple[1]


class StateGraph(ABC):
    START_STATE = "_S_"
    END_STATE = "_E_"

    def __init__(self, autobuild=True):
        self.graph = networkx.DiGraph()
        self.graph.add_node(StateGraph.START_STATE)
        self.graph.add_node(StateGraph.END_STATE)

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
        return self.graph[self.current_state]

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
        old_history = self.history.copy()
        if self.done:
            if reset:
                self.reset()
            else:
                return PathResult((False, None), old_history)

        r = None
        for i, action in enumerate(path):
            if not self.step(action):
                r = PathResult((False, action), old_history)

        if r is None:
            r = PathResult((self.done, None), old_history)

        if reset:
            self.reset()

        return r

    def __str__(self):
        return str(self.graph)

    def __repr__(self):
        return str(self.graph)


class MSG(StateGraph):
    def build(self):
        self.graph.add_edges_from(
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


def main():
    fsm = MSG()

    path = ["A", "B", "C", "A", "D", StateGraph.END_STATE]
    print(fsm.take_path(path, reset=False).success)
    print(fsm.history)


if __name__ == "__main__":
    main()
