import networkx as nx
from abc import ABCMeta, abstractmethod
from typing import NamedTuple
from pathlib import Path
from matplotlib import pyplot as plt
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

    def cycle_detect(self, path=None):
        """if path is given, it only returns cycles actually in path, that is, a cycle taken."""
        cycle = nx.find_cycle(self, path)
        if path:
            # flatten list[tuple] to list and compare to path
            return [n for n, _ in cycle if n in path]
        else:
            return cycle

    def walk(self, path, reset=True):
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

        if autoshow:
            plt.show()

    def animate(
        self, path: list[STATE_TYPE], autoshow=False, save_img: Path | None = None
    ):
        self.reset()

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # generate affixed positions for the nodes
        pos = nx.spring_layout(self)

        def update(i):
            ax.clear()
            self.step(path[i], verbose=True)
            self.draw(ax=ax, pos=pos)
            ax.set_title(f"Step {i}: {self.current_state}")

        ani = animation.FuncAnimation(
            fig, update, frames=len(path), interval=1000, repeat=True
        )

        if save_img:
            ani.save(save_img, writer="imagemagick", fps=1)

        if autoshow:
            # Note: broken for some reason
            plt.show()

        return ani
