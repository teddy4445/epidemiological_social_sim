# library imports
import random

# project imports
from node import Node
from edge import Edge


class Graph:
    """
    A graph object
    """

    def __init__(self,
                 nodes: list,
                 epi_edges: list,
                 socio_edges: list):
        self.nodes = nodes
        self.epi_edges = epi_edges
        self.socio_edges = socio_edges

        self._locked_next_nodes_epi = None
        self._locked_next_nodes_social = None

    def get_size(self) -> int:
        return len(self.nodes)

    def next_nodes_epi(self,
                       id: int):
        try:
            return self._locked_next_nodes_epi[id]
        except:
            self.prepare_next_nodes_epi()
            # now when the member is ready
            return self.next_nodes_epi(id=id)

    def prepare_next_nodes_epi(self):
        self._locked_next_nodes_epi = {}
        for edge in self.epi_edges:
            try:
                self._locked_next_nodes_epi[edge.s_id].append(edge.t_id)
            except:
                self._locked_next_nodes_epi[edge.s_id] = [edge.t_id]

    def next_nodes_socio(self,
                         id: int):
        try:
            return self._locked_next_nodes_social[id]
        except:
            self.prepare_next_nodes_socio()
            # now when the member is ready
            return self.next_nodes_epi(id=id)

    def prepare_next_nodes_socio(self):
        self._locked_next_nodes_social = {}
        for edge in self.socio_edges:
            try:
                self._locked_next_nodes_social[edge.s_id].append(edge.t_id)
            except:
                self._locked_next_nodes_social[edge.s_id] = [edge.t_id]

    def get_items(self,
                  ids: list):
        return [self.nodes[id] for id in ids]

    @staticmethod
    def generate_random(node_count: int,
                        epi_edge_count: int,
                        socio_edge_count: int):
        """
        Generate random graph with a given number of nodes and edges
        """
        nodes = [Node.create_random_mostly_s(id=id) for id in range(node_count)]
        epi_edges = []
        while len(epi_edges) < epi_edge_count:
            s_id = random.randint(0, node_count - 1)
            t_id = random.randint(0, node_count - 1)
            if s_id != t_id and Edge(s_id=s_id, t_id=t_id, w=0) not in epi_edges:
                epi_edges.append(Edge(s_id=s_id, t_id=t_id, w=1))
        socio_edges = []
        while len(socio_edges) < socio_edge_count:
            s_id = random.randint(0, node_count - 1)
            t_id = random.randint(0, node_count - 1)
            if s_id != t_id and Edge(s_id=s_id, t_id=t_id, w=0) not in socio_edges:
                socio_edges.append(Edge(s_id=s_id, t_id=t_id, w=1))
        return Graph(nodes=nodes,
                     epi_edges=epi_edges,
                     socio_edges=socio_edges)

    @staticmethod
    def fully_connected(node_count: int):
        """
        Generate a fully connected graph with a given number of nodes
        """
        nodes = [Node.create_random_mostly_s(id=id) for id in range(node_count)]
        epi_edges = []
        socio_edges = []
        for i in range(node_count):
            for j in range(node_count):
                if i != j:
                    epi_edges.append(Edge(s_id=i, t_id=j, w=1))
        for i in range(node_count):
            for j in range(node_count):
                if i != j:
                    socio_edges.append(Edge(s_id=i, t_id=j, w=1))
        return Graph(nodes=nodes,
                     epi_edges=epi_edges,
                     socio_edges=socio_edges)

    def __hash__(self):
        return (self.nodes, self.epi_edges, self.socio_edges).__hash__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<Graph: V={}, E_e={}, E_s={}>".format(len(self.nodes),
                                                      len(self.epi_edges),
                                                      len(self.socio_edges))
