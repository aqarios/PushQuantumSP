import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.cm as cm

class SPPlot():
    def __init__(self, data, evaluation=None):
        self.data = data
        self.evaluation = evaluation

    def plot_solution(self, hide_never_covered=True):
        fig, ax = plt.subplots()
        pos = {node: node for node in self.data.G.nodes()}
        pos_opt = {node: node for node in self.evaluation.O.nodes()}

        if hide_never_covered:
            street_points_covered = set(self.data.listStreetPoints3D) - set(self.data.listStreetPointsNeverCovered)
            nx.draw_networkx_nodes(self.data.G, pos, nodelist=list(street_points_covered), node_color='blue', node_size=40, ax=ax)
        else:
            nx.draw_networkx_nodes(self.data.G, pos, self.data.listStreetPoints3D, node_color='blue', node_size=40, ax=ax)
            nx.draw_networkx_nodes(self.data.G, pos, self.data.listStreetPointsNeverCovered, node_color='red', node_size=10, ax=ax)

        nx.draw_networkx_nodes(self.evaluation.O, pos_opt, self.evaluation.listStreetPointsCovered, node_color='green', node_size=40, ax=ax)
        nx.draw_networkx_nodes(self.data.G, pos, self.data.listLidar3D, node_color='orange', node_size=40, ax=ax)
        nx.draw_networkx_nodes(self.evaluation.O, pos_opt, self.evaluation.listLidarActivated, node_color='red', node_size=40, ax=ax)

        posw = {node: node for node in self.data.M.nodes()}
        edw = {node: node for node in self.data.M.edges()}

        nx.draw_networkx_edges(self.data.M, posw, edw, width=5.0, alpha=1, edge_color='black', ax=ax)

        ax.axis('equal')
        ax.grid(True)

        ax.set_title("Solution")
        ax.text(
            0.5, -0.05,
            f'Activated Lidars: {self.evaluation.get_objective()} \n missing achievable coverage: {self.evaluation.check_solution()["missing_achievable_coverage"]}',
            fontsize=10, ha='center', va='top', transform=ax.transAxes
        )

        return fig

    def plot_problem(self, draw_connections=True, hide_never_covered=True, show=False):
        fig, ax = plt.subplots()
        pos = {node: node for node in self.data.G.nodes()}

        if hide_never_covered:
            street_points_covered = set(self.data.listStreetPoints3D) - set(self.data.listStreetPointsNeverCovered)
            nx.draw_networkx_nodes(self.data.G, pos, nodelist=list(street_points_covered), node_color='blue', node_size=40, ax=ax)
        else:
            nx.draw_networkx_nodes(self.data.G, pos, self.data.listStreetPoints3D, node_color='blue', node_size=40, ax=ax)
            nx.draw_networkx_nodes(self.data.G, pos, self.data.listStreetPointsNeverCovered, node_color='red', node_size=10, ax=ax)

        nx.draw_networkx_nodes(self.data.G, pos, self.data.listLidar3D, node_color='orange', node_size=40, ax=ax)

        posw = {node: node for node in self.data.M.nodes()}
        edw = {node: node for node in self.data.M.edges()}
        nx.draw_networkx_edges(self.data.M, posw, edw, width=5.0, alpha=1, edge_color='black', ax=ax)

        if draw_connections:
            posl = {(node[0], node[1]): (node[0], node[1]) for node in self.data.G.nodes()}
            edl = {((node[0][0], node[0][1]), (node[1][0], node[1][1])): (node[0], node[1]) for node in self.data.G.edges()}
            nx.draw_networkx_edges(self.data.G, posl, edl, width=2.0, alpha=0.5, edge_color='green', ax=ax)

        ax.axis('equal')
        ax.grid(True)

        return fig

    def plot_partitioned_graph(self, partitions, cut_edges):
        """
        Plot the graph with partitions highlighted.

        Parameters:
        - partitions: List of sets, each containing nodes in a partition.
        - cut_edges: List of edges that are cut (inter-partition edges).

        Returns:
        - fig: The matplotlib figure object with the plot.
        """
        fig, ax = plt.subplots()
        G = self.data.G

        # Generate positions ensuring consistent dimensionality
        pos = {node: (node[0], node[1]) for node in G.nodes()}  # Use (x, y) for all nodes

        # Assign unique colors to each partition
        if len(partitions) <= 10:
            cmap = cm.get_cmap("tab10")
            colors = [cmap(i) for i in range(len(partitions))]
        else:
            cmap = cm.get_cmap("viridis", len(partitions))
            colors = [cmap(i) for i in range(len(partitions))]

        # Plot partitions
        for i, part in enumerate(partitions):
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=list(part),
                node_color=[colors[i]] * len(part),
                node_size=50,
                label=f"Partition {i+1}",
                ax=ax
            )

        # Plot intra-partition edges
        for i, part in enumerate(partitions):
            subgraph = G.subgraph(part)
            nx.draw_networkx_edges(G, pos, edgelist=subgraph.edges(), edge_color=colors[i], alpha=0.7, width=2.0, ax=ax)

        # Plot cut edges (inter-partition edges)
        nx.draw_networkx_edges(G, pos, edgelist=cut_edges, edge_color="red", alpha=0.9, width=2.5, label="Cut Edges", ax=ax)

        # Add grid, legend, and title
        ax.axis("equal")
        ax.grid(True)
        ax.legend(loc="best")
        ax.set_title("Partitioned Graph with Minimal Cuts")

        return fig
