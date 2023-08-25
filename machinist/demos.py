from pathlib import Path
from matplotlib import pyplot as plt
import networkx as nx

from .stategraph import StateGraph
from .walkers.greedy import greedy_path
from .builders.autosg import AutoSG


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


def fsm_animate_demo():
    fsm = MSG()
    path = ["A", "B", "C", "A", "D", StateGraph.END_STATE]
    ani = fsm.animate(path, save_img=Path("out/basic_fsm_demo.gif"))
    plt.close()
    print(fsm.cycle_detect(path))


def fsm_shortest_walk_demo():
    fsm = MSG()
    path = nx.shortest_path(fsm, StateGraph.START_STATE, StateGraph.END_STATE)
    ani = fsm.animate(path, save_img=Path("out/basic_fsm_demo_shortest.gif"))
    plt.close()


def fsm_greedy_walk_demo():
    fsm = AutoSG().build(n=40, target_avg_degree=5, graph_type="random")
    path = greedy_path(fsm, StateGraph.START_STATE)
    ani = fsm.animate(path, save_img=Path("out/greedy_demo.gif"))
    plt.close()


def basic_fsm_demo():
    fsm = MSG()
    path = ["A", "B", "C", "A", "D", StateGraph.END_STATE]
    result = fsm.walk(path, reset=False)
    print(f"{result}\nHistory: {fsm.history} (Should match path_taken)")

    fsm.reset()
    fsm.walk(result.path_taken)
    print(
        f"Post reset: (using the old path taken as input)\n{result}\nHistory: {fsm.history} (Should match path_taken)"
    )


def autosg_demo():
    types = ["random", "cycle", "star", "grid", "complete"]

    for t in types:
        plt.close()
        G = AutoSG().build(n=40, target_avg_degree=5, graph_type=t)
        pos = nx.spring_layout(G)
        nx.draw_networkx(G, pos=pos)
        plt.savefig(f"out/autosg_{t}.png")
        try:
            p = nx.shortest_path(G, StateGraph.START_STATE, StateGraph.END_STATE)
            G.animate(p, save_img=Path(f"out/autosg_{t}_shortest_walk.gif"))
        except nx.exception.NetworkXNoPath:
            print(
                f"Graph {t} has no path from start to end! Dang dirty directed graphs!"
            )
