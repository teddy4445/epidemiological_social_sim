# library imports
import os
import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt

# project imports
from graph import Graph
from sim import Simulator


class Plotter:
    """
    A class to generate graphs from the simulation's data
    """

    COLORS = ["#34A853", "#FBBC05", "#EA4335", "#7a150d", "#4285F4", "#a83489", "#111111"]
    STYLES = ["-o", "-s", "-^", "--^", "-P", "--P", "-D"]
    LABELS = ["S", "E", "$I^a$", "$I^s$", "$R^f$", "$R^p$", "D"]

    def __init__(self):
        pass

    @staticmethod
    def show_graph_connectivity(graph: Graph,
                                save_path: str,
                                bins_count: int = 50):
        """
        Plot the graph's social and epidemiological connectivity
        """
        plt.hist([len(graph.next_nodes_epi(id=node.id)) for node in graph.nodes], bins_count, density=True, facecolor='r', alpha=0.5, label="Epidemiological")
        plt.hist([len(graph.next_nodes_socio(id=node.id)) for node in graph.nodes], bins_count, density=True, facecolor='b', alpha=0.5, label="Social")
        plt.xlabel('Connections')
        plt.ylabel('Count')
        plt.grid(alpha=0.2,
                 color="black")
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def show_graph(graph: Graph,
                   save_path: str):
        """
        Plot the graph as both social and epidemiological graphs
        """
        G = nx.DiGraph()
        # create the graph
        node_color = []
        for node in graph.nodes:
            G.add_node(node.id,
                       is_virtual=node.is_virtual,
                       state=node.e_state)
            node_color.append(Plotter.COLORS[int(node.e_state)])
        [G.add_edge(u_of_edge=edge.s_id,
                    v_of_edge=edge.t_id,
                    is_social=True)
         for edge in graph.socio_edges]
        [G.add_edge(u_of_edge=edge.s_id,
                    v_of_edge=edge.t_id,
                    is_social=False)
         for edge in graph.epi_edges]
        # Draw settings
        colors = ["b" if is_social else "r" for is_social in nx.get_edge_attributes(G, 'is_social').values()]
        # Draw image
        nx.draw_circular(G,
                         font_color='white',
                         node_color=node_color,
                         edge_color=colors,
                         with_labels=True)
        plt.savefig(save_path)
        plt.close()

    @staticmethod
    def compare_plot(x: list,
                     y: list,
                     y_err: list,
                     y_label: str,
                     x_label: str,
                     save_path: str,
                     normalized: bool = False):
        """
        Plot a compare bar figure
        """
        plt.bar(range(len(x)),
                y,
                width=0.8,
                color=Plotter.COLORS[3])
        plt.errorbar(list(range(len(x))),
                     y,
                     yerr=y_err,
                     fmt="-o",
                     linewidth=0,
                     elinewidth=1,
                     markersize=1,
                     capsize=4,
                     ecolor="black")
        plt.ylabel(y_label, fontsize=16)
        plt.xlabel(x_label, fontsize=16)
        plt.xticks(range(len(x)), x, fontsize=12)
        ax = plt.gca()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        if normalized:
            plt.ylim((0, 1))
        plt.grid(alpha=0.2,
                 axis="y",
                 color="black")
        plt.tight_layout()
        plt.savefig(save_path, dpi=600)
        plt.close()

    @staticmethod
    def basic_sim_plots(sim: Simulator,
                        save_path: str):
        """
        Plot distribution over time of locations and epidemiological state
        """
        data = np.asarray(sim.epi_dist)
        for epi_state in range(len(data[0])):
            plt.plot(range(len(data)),
                     data[:, epi_state] / sim.graph.get_size(),
                     Plotter.STYLES[epi_state],
                     color=Plotter.COLORS[epi_state],
                     label=Plotter.LABELS[epi_state],
                     markersize=4)
        plt.xlabel("Simulation step", fontsize=16)
        plt.ylabel("Epidemiological state distribution", fontsize=16)
        plt.yticks([0.1 * i for i in range(11)])
        plt.xlim((-1, sim.max_time + 1))
        plt.grid(alpha=0.2,
                 color="black")
        plt.legend()
        ax = plt.gca()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()
        plt.savefig(save_path, dpi=600)
        plt.close()

    @staticmethod
    def ideas_plots(sim: Simulator,
                    save_path: str):
        """
        Plot distribution over time of locations and epidemiological state
        """
        data_mean = np.asarray(sim.ideas_dist_mean)
        data_std = np.asarray(sim.ideas_dist_std)
        for idea_state in range(len(data_mean[0])):
            # the line
            plt.plot(range(len(data_mean)),
                     data_mean[:, idea_state],
                     Plotter.STYLES[idea_state],
                     color=Plotter.COLORS[idea_state],
                     label="Idea #{}".format(idea_state),
                     markersize=4)
            # the STD
            plt.fill_between(
                range(len(data_mean)),
                data_mean[:, idea_state] - data_std[:, idea_state],
                data_mean[:, idea_state] + data_std[:, idea_state],
                color=Plotter.COLORS[idea_state],
                alpha=0.2
            )
        plt.xlabel("Simulation step", fontsize=16)
        plt.ylabel("Ideas state distribution", fontsize=16)
        plt.yticks([0.1 * i for i in range(11)])
        plt.xlim((-1, sim.max_time + 1))
        plt.ylim((0, 1))
        plt.grid(alpha=0.2,
                 color="black")
        plt.legend()
        ax = plt.gca()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()
        plt.savefig(save_path, dpi=600)
        plt.close()

    @staticmethod
    def sensitivity_heatmap(data: pd.DataFrame,
                            xlabel: str,
                            ylabel: str,
                            save_path: str):
        """
        Plot heatmap of the given data
        """
        sns.heatmap(data, annot=False, cmap="coolwarm")
        plt.xlabel(xlabel, fontsize=16)
        plt.ylabel(ylabel, fontsize=16)
        plt.savefig(save_path, dpi=600)
        plt.close()
