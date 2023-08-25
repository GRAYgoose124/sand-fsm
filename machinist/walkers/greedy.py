def greedy_path(G, start_node):
    visited = set()
    path = [start_node]
    current = start_node

    while True:
        visited.add(current)
        neighbors = set(G[current]) - visited

        if not neighbors:
            break

        next_node = max(neighbors, key=lambda n: G[current][n].get("weight", 1))
        path.append(next_node)
        current = next_node

    return path
