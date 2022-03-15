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
        Main.simple()

    @staticmethod
    def simple():
        """
        The simplest case
        """
        print("Main.simple_seird: running")
        sim = SimulatorGenerator.simple_random(node_count=100,
                                               epi_edge_count=100*25,
                                               socio_edge_count=100*25,
                                               max_time=200)
        sim.run()
        Plotter.basic_sim_plots(sim=sim,
                                save_path=os.path.join(Main.RESULTS_FOLDER, "simple.png"))

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
