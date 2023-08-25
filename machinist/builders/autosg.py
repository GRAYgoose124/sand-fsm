from random import randint

from ..stategraph import StateGraph


class AutoSG(StateGraph):
    START_STATE = "_S_"
    END_STATE = "_E_"

    # please dear god make sure labeler is ordered
    def build(self, n=10, target_avg_degree=5, labeler=str, graph_type="random"):
        first = labeler(0)
        last = labeler(n - 1)

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

        nlist = list(self.nodes)
        # if start and end's don't have at least 1 edge, add one
        if self.degree(StateGraph.END_STATE) == 0:
            self.add_edge(last, StateGraph.END_STATE)

        if self.degree(StateGraph.START_STATE) == 0:
            self.add_edge(StateGraph.START_STATE, first)

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
