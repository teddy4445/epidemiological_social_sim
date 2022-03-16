# library imports
import os
import numpy as np
import matplotlib.pyplot as plt

# project imports
from graph import Graph
from sim import Simulator


class Plotter:
    """
    A class to generate graphs from the simulation's data
    """

    COLORS = ["#34A853", "#FBBC05", "#EA4335", "#4285F4", "#111111", "#a83489"]
    STYLES = ["-o", "-s", "-^", "-P", "-D", "--"]
    LABELS = ["S", "E", "I", "R", "D", "V"]

    def __init__(self):
        pass

    @staticmethod
    def compare_plot(x: list,
                     y: list,
                     y_err: list,
                     y_label: str,
                     x_label: str,
                     save_path: str,
                     normalized: bool = False):
        """
        plot a compare bar figure
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
