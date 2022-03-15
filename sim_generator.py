# library imports

# project imports
from graph import Graph
from pips.pip import PIP
from sim import Simulator


class SimulatorGenerator:
    """
    A class to generate simulation settings
    """

    def __init__(self):
        pass

    @staticmethod
    def simple_random(node_count: int = 50,
                      epi_edge_count: int = 1000,
                      socio_edge_count: int = 1000,
                      max_time: int = 200):
        graph = Graph.generate_random(node_count=node_count,
                                      epi_edge_count=epi_edge_count,
                                      socio_edge_count=socio_edge_count)
        return Simulator(graph=graph,
                         pip=PIP(),
                         max_time=max_time)

    @staticmethod
    def full_connected(node_count: int = 50,
                       edge_count: int = 0,
                       max_time: int = 200):
        graph = Graph.fully_connected(node_count=node_count)
        return Simulator(graph=graph,
                         pip=PIP(),
                         max_time=max_time)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<SimulatorGenerator>"
