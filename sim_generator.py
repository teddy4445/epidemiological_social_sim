# library imports
import os
import math
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
    def facebook(max_time: int = 200):
        random.seed(73)  # SHELDON's number so the graph will be always the same

        socio_edges = []
        with open(os.path.join(os.path.dirname(__file__), "data", "facebook.txt"), "r") as graph_edges:
            for line in graph_edges.readlines():
                vals = line.strip().split(" ")
                if len(vals) == 2:
                    socio_edges.append(Edge(s_id=int(vals[0])-1,
                                            t_id=int(vals[1])-1,
                                            w=1))
        # add more physical as it happens more often than just social
        FACEBOOK_GRAPH_NODES = 4039
        FACEBOOK_MEET_CHANCE = 0.1
        epi_edges = [edge.copy() for edge in socio_edges if random.random() < FACEBOOK_MEET_CHANCE]  # if friends in facebook we believe in 10% they will meet
        epi_end_size = round(math.sqrt(2)/FACEBOOK_MEET_CHANCE * len(epi_edges)) # we assume sqrt(2) more physical than social meetings
        while len(epi_edges) < epi_end_size:
            s_id = random.randint(0, FACEBOOK_GRAPH_NODES - 1)
            t_id = random.randint(0, FACEBOOK_GRAPH_NODES - 1)
            if s_id != t_id and Edge(s_id=s_id, t_id=t_id, w=0) not in epi_edges:
                epi_edges.append(Edge(s_id=s_id, t_id=t_id, w=1))
        # create graph
        graph = Graph(nodes=[Node.create_random_mostly_s(id=id) for id in range(FACEBOOK_GRAPH_NODES)],
                      socio_edges=socio_edges,
                      epi_edges=epi_edges)
        return Simulator(graph=graph,
                         pip=PIP(),
                         max_time=max_time)

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
                                    epidimiological_state=EpidemiologicalState.S))
            socio_edges = []
            while len(socio_edges) < round(socio_edge_count * anti_virtual_nodes / node_count):
                t_id = random.randint(0, node_count - 1)
                if s_id != t_id and Edge(s_id=s_id, t_id=t_id, w=0) not in socio_edges:
                    socio_edges.append(Edge(s_id=s_id, t_id=t_id, w=1))
            graph.socio_edges.extend(socio_edges)
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
