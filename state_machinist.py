from abc import ABC, ABCMeta, abstractmethod
from pathlib import Path
from typing import NamedTuple
from matplotlib import pyplot as plt
import networkx as nx
import matplotlib.animation as animation


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
    STATE_TYPE = str

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
            return None

        if self.can_step(action):
            self.history.append(action)

            return self
        else:
            return None

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

    def draw(self, *args, autoshow=False, save_img: Path | None = None, **kwargs):
        """Draw the graph using networkx"""
        # make the current node red
        node_colors = ["red" if n == self.current_state else "blue" for n in self.nodes]
        # make the links taken green
        edge_colors = [
            "green" if (u, v) in zip(self.history[:-1], self.history[1:]) else "black"
            for u, v in self.edges
        ]

        nx.draw_networkx(
            self, *args, node_color=node_colors, edge_color=edge_colors, **kwargs
        )

        if save_img:
            plt.savefig(save_img)
            plt.close()

        if autoshow:
            plt.show()

    def animate(self, path: list[STATE_TYPE]):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # generate affixed positions for the nodes
        pos = nx.spring_layout(self)

        def update(i):
            ax.clear()

            self.step(path[i], verbose=True)
            self.draw(ax=ax, pos=pos)
            ax.set_title(f"Step {i}: {self.current_state}")

        return animation.FuncAnimation(
            fig, update, frames=len(self), interval=1000, repeat=True
        )


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
            if i != j and abs(i - j) % (1 / connectivity) == 0:
                G.add_edge(i, j)

    return G


def basic_fsm_demo():
    fsm = MSG()

    path = ["A", "B", "C", "A", "D", StateGraph.END_STATE]
    # result = fsm.take_path(path, reset=False)
    # print(f"{result}\nHistory: {fsm.history} (Should match path_taken)")

    # fsm.reset()
    # fsm.take_path(result.path_taken)
    # print(
    #     f"Post reset: (using the old path taken as input)\n{result}\nHistory: {fsm.history} (Should match path_taken)"
    # )

    # Lets use FuncAnimation to animate the graph
    ani = fsm.animate(path)
    ani.save("basic_fsm_demo.gif", writer="imagemagick", fps=1)


def main():
    basic_fsm_demo()

    # G = sparse_builder()
    # nx.draw_networkx(G)
    # plt.show()


if __name__ == "__main__":
    main()
