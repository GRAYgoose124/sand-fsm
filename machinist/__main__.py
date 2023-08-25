import networkx as nx

from pathlib import Path
from matplotlib import pyplot as plt

from .stategraph import StateGraph
from .builders.autosg import AutoSG

from .demos import (
    basic_fsm_demo,
    fsm_animate_demo,
    autosg_demo,
    fsm_shortest_walk_demo,
    fsm_greedy_walk_demo,
)

from .walkers.greedy import greedy_path
from .walkers.aco import aco_path


def argparser():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--demo",
        type=int,
        default=0,
        choices=range(5),
        help="Which demo to run ((0, basic_fsm_demo), (1, fsm_animate_demo), (2, fsm_shortest_walk_demo), (3, fsm_greedy_walk_demo), (4, autosg_demo))",
    )
    return parser.parse_args()


def main():
    root = (Path(__file__).parent / "out").resolve()
    if not root.exists():
        root.mkdir()

    args = argparser()

    [
        basic_fsm_demo,
        fsm_animate_demo,
        fsm_shortest_walk_demo,
        fsm_greedy_walk_demo,
        autosg_demo,
    ][args.demo]()


if __name__ == "__main__":
    main()
