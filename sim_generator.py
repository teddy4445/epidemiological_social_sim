# library imports
import random

# project imports
from edge import Edge
from node import Node
from graph import Graph
from pips.pip import PIP
from sim import Simulator
from epidemiological_state import EpidemiologicalState


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
    def anti_vaccine_simple_random(node_count: int = 50,
                                   anti_virtual_nodes: int = 10,
                                   epi_edge_count: int = 1000,
                                   socio_edge_count: int = 1000,
                                   max_time: int = 200):
        graph = Graph.generate_random(node_count=node_count,
                                      epi_edge_count=epi_edge_count,
                                      socio_edge_count=socio_edge_count)
        for i in range(anti_virtual_nodes):
            s_id = node_count + i
            graph.nodes.append(Node(id=s_id,
                                    is_virtual=True,
                                    ideas=[0.5, 0.5, 0],
                                    personality_vector=[],
                                    timer=0,
                                    epidimiological_state=EpidemiologicalState.V))
            socio_edges = []
            while len(socio_edges) < round(socio_edge_count * anti_virtual_nodes / node_count):
                t_id = random.randint(0, node_count - 1)
                if s_id != t_id and Edge(s_id=s_id, t_id=t_id, w=0) not in socio_edges:
                    socio_edges.append(Edge(s_id=s_id, t_id=t_id, w=1))
            graph.socio_edgee.extend(socio_edges)
        # return answer
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
