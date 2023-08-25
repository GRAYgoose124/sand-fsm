from abc import ABC, ABCMeta, abstractmethod
from itertools import combinations
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
            fig, update, frames=len(self), interval=1000, repeat=True
        )

        if save_img:
            ani.save(save_img, writer="imagemagick", fps=1)

        if autoshow:
            # Note: broken for some reason
            plt.show()

        return ani


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


from random import randint, choice


class AutoSG(StateGraph):
    START_STATE = "_S_"
    END_STATE = "_E_"

    def build(self, n=10, target_avg_degree=5, labeler=str, graph_type="random"):
        for i in range(n):
            self.add_node(labeler(i))

        if graph_type == "random":
            self.build_random_graph(n, target_avg_degree, labeler)
        elif graph_type == "cycle":
            self.build_cycle_graph(n, labeler)
        elif graph_type == "complete":
            self.build_complete_graph(n, labeler)
        elif graph_type == "grid":
            self.build_grid_graph(n, labeler)
        elif graph_type == "star":
            self.build_star_graph(n, labeler)
        else:
            print("Unknown graph type!")

        return self

    def build_random_graph(self, n, target_avg_degree, labeler):
        for i in range(n):
            for j in range(i + 1, n):
                if randint(0, n) < target_avg_degree:
                    self.add_edge(labeler(i), labeler(j))

    def build_cycle_graph(self, n, labeler):
        for i in range(n):
            self.add_edge(labeler(i), labeler((i + 1) % n))

    def build_complete_graph(self, n, labeler):
        for i in range(n):
            for j in range(i + 1, n):
                self.add_edge(labeler(i), labeler(j))

    def build_grid_graph(self, n, labeler):
        side = int(n**0.5)
        for i in range(side):
            for j in range(side):
                cur = i * side + j
                if i > 0:
                    self.add_edge(labeler(cur), labeler(cur - side))
                if i < side - 1:
                    self.add_edge(labeler(cur), labeler(cur + side))
                if j > 0:
                    self.add_edge(labeler(cur), labeler(cur - 1))
                if j < side - 1:
                    self.add_edge(labeler(cur), labeler(cur + 1))

    def build_star_graph(self, n, labeler):
        center = labeler(0)
        for i in range(1, n):
            self.add_edge(center, labeler(i))


def sparse_builder(G=MSG(), connectivity=0.5, nodes=10):
    for i in range(nodes):
        G.add_node(i)

    for i in range(nodes):
        for j in range(nodes):
            if i != j and abs(i - j) % (1 / connectivity) == 0:
                G.add_edge(i, j)

    return G


def fsm_animate_demo():
    fsm = MSG()
    path = ["A", "B", "C", "A", "D", StateGraph.END_STATE]
    ani = fsm.animate(path, save_img=Path("basic_fsm_demo.gif"))

    print(fsm.cycle_detect(path))
    plt.close()


def basic_fsm_demo():
    fsm = MSG()
    path = ["A", "B", "C", "A", "D", StateGraph.END_STATE]
    result = fsm.take_path(path, reset=False)
    print(f"{result}\nHistory: {fsm.history} (Should match path_taken)")

    fsm.reset()
    fsm.walk(result.path_taken)
    print(
        f"Post reset: (using the old path taken as input)\n{result}\nHistory: {fsm.history} (Should match path_taken)"
    )


def main():
    # basic_fsm_demo()
    # fsm_animate_demo()

    # Sparse test
    # G = sparse_builder()
    # nx.draw_networkx(G)
    # plt.show()

    # AutoSG
    types = ["random", "cycle", "star", "grid", "complete"]

    for t in types:
        plt.close()
        G = AutoSG().build(n=40, target_avg_degree=5, graph_type=t)
        pos = nx.spring_layout(G)
        nx.draw_networkx(G, pos=pos)
        plt.savefig(f"autosg_{t}.png")


if __name__ == "__main__":
    main()
