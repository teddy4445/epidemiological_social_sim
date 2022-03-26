# library imports
import os
import gc
import json
import numpy as np
import pandas as pd

# project imports
from sim import Simulator
from plotter import Plotter
from sim_generator import SimulatorGenerator


class Main:
    """
    Single entry point of the project
    """

    # CONSTS #
    RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "results")
    # END - CONSTS #

    def __init__(self):
        pass

    @staticmethod
    def run():
        """
        Run all the experiments one after the other
        """
        Main.io_prepare()
        #Main.simple()
        #Main.simple_anti_vaccine()
        #Main.facebook_graph()

        # sensitivity analysis
        Main.sensitivity_of_r_zero_over_connectivity()

    @staticmethod
    def simple():
        """
        The simplest case
        """
        print("Main.simple: running")
        sim = SimulatorGenerator.simple_random(node_count=100,
                                               epi_edge_count=100 * 10,
                                               socio_edge_count=100 * 25,
                                               max_time=30)
        sim.run()
        # plot results
        Plotter.show_graph_connectivity(graph=sim.graph,
                                        bins_count=50,
                                        save_path=os.path.join(Main.RESULTS_FOLDER, "simple_graph_connectivity.png"))
        Plotter.show_graph(graph=sim.graph,
                           save_path=os.path.join(Main.RESULTS_FOLDER, "simple_graph.png"))
        Plotter.basic_sim_plots(sim=sim,
                                save_path=os.path.join(Main.RESULTS_FOLDER, "simple_epi.png"))
        Plotter.ideas_plots(sim=sim,
                            save_path=os.path.join(Main.RESULTS_FOLDER, "simple_ideas.png"))

    @staticmethod
    def simple_anti_vaccine():
        """
        The simplest case - with anti vaccine influence
        """
        print("Main.simple_anti_vaccine: running")
        sim = SimulatorGenerator.anti_vaccine_simple_random(node_count=100,
                                                            anti_virtual_nodes=10,
                                                            epi_edge_count=100 * 11,
                                                            socio_edge_count=100 * 11,
                                                            max_time=150)
        sim.run()
        Plotter.basic_sim_plots(sim=sim,
                                save_path=os.path.join(Main.RESULTS_FOLDER, "simple_anti_vaccine_epi.png"))
        Plotter.ideas_plots(sim=sim,
                            save_path=os.path.join(Main.RESULTS_FOLDER, "simple_anti_vaccine_ideas.png"))

    @staticmethod
    def facebook_graph():
        """
        Load the graph from Facebook about social networks
        # source: https://snap.stanford.edu/data/egonets-Facebook.html
        """
        print("Main.facebook_graph: running")
        facebook_model = os.path.join(os.path.dirname(__file__), "results", "facebook_sim")
        if not os.path.exists(facebook_model):
            sim = SimulatorGenerator.facebook(max_time=180)
            sim.graph.prepare_next_nodes_epi()
            sim.graph.prepare_next_nodes_socio()
            sim.save(path=facebook_model)
        else:
            sim = Simulator.load(path=facebook_model)
        sim.run()
        Plotter.basic_sim_plots(sim=sim,
                                save_path=os.path.join(Main.RESULTS_FOLDER, "facebook_graph.png"))
        Plotter.ideas_plots(sim=sim,
                            save_path=os.path.join(Main.RESULTS_FOLDER, "facebook_graph_ideas.png"))

    @staticmethod
    def sensitivity_of_r_zero_over_connectivity():
        """
        The simplest case
        """
        print("Main.sensitivity_of_r_zero_over_connectivity: running")
        # avoid inner sim prints
        Simulator.DEBUG = False
        max_time = 150
        node_count = 50
        samples_count = 10
        repeat_count = 5
        max_edges = node_count * node_count
        # gather data
        r_zeros_means = np.zeros((samples_count-1, samples_count-1), dtype=float)
        r_zeros_stds = np.zeros((samples_count-1, samples_count-1), dtype=float)
        for i, social_edges in enumerate(range(round(max_edges/samples_count), round(max_edges), round(max_edges/samples_count))):
            for j, epi_edges in enumerate(range(round(max_edges/samples_count), round(max_edges), round(max_edges/samples_count))):
                print("Working on {}X{} ({}X{})".format(social_edges, epi_edges, i, j))
                answers = []
                for repeat_index in range(repeat_count):
                    print("Repeat #{}/{} ({:.2f})".format(repeat_index+1, repeat_count, (1+repeat_index)*100/repeat_count))
                    sim = SimulatorGenerator.simple_random(node_count=node_count,
                                                           epi_edge_count=epi_edges,
                                                           socio_edge_count=social_edges,
                                                           max_time=max_time)
                    sim.run(stop_early=True)
                    answers.append(sim.mean_r_zero())
                    # free memory each time
                    del sim
                    gc.collect()
                r_zeros_means[i][j] = np.mean(answers)
                r_zeros_stds[i][j] = np.std(answers)
        # save raw data
        with open(os.path.join(Main.RESULTS_FOLDER, "raw_r_zeros_results.json"), "w") as results_file:
            json.dump({"means": r_zeros_means.tolist(), "stds": r_zeros_stds.tolist()}, results_file)
        # plot heatmaps
        Plotter.sensitivity_heatmap(data=pd.DataFrame(data=r_zeros_means,
                                                      index=[round(1/samples_count*(i+1), 2) for i in range(samples_count-1)],
                                                      columns=[round(1/samples_count*(i+1), 2) for i in range(samples_count-1)]),
                                    xlabel="Social edges portion",
                                    ylabel="Epidemiological edges portion",
                                    save_path=os.path.join(Main.RESULTS_FOLDER, "r_zeros_means.png"))
        Plotter.sensitivity_heatmap(data=pd.DataFrame(data=r_zeros_stds,
                                                      index=[round(1/samples_count*(i+1), 2) for i in range(samples_count-1)],
                                                      columns=[round(1/samples_count*(i+1), 2) for i in range(samples_count-1)]),
                                    xlabel="Social edges portion",
                                    ylabel="Epidemiological edges portion",
                                    save_path=os.path.join(Main.RESULTS_FOLDER, "r_zeros_stds.png"))

    @staticmethod
    def io_prepare():
        """
        Make sure we have all the IO stuff we need
        """
        try:
            os.mkdir(Main.RESULTS_FOLDER)
        except:
            pass


if __name__ == '__main__':
    Main.run()
