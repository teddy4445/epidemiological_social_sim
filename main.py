# library imports
import os
import time
import random
import numpy as np

# project imports
from sim import Simulator
from plotter import Plotter
from multi_sim import MultiSim
from sim_generator import SimulatorGenerator


class Main:
    """
    Single entry point of the project
    """

    RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), "results")

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
        Main.facebook_graph()

    @staticmethod
    def simple():
        """
        The simplest case
        """
        print("Main.simple: running")
        sim = SimulatorGenerator.simple_random(node_count=100,
                                               epi_edge_count=100 * 25,
                                               socio_edge_count=100 * 25,
                                               max_time=150)
        sim.run()
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
