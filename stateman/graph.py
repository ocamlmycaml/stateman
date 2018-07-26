import networkx as nx

from stateman.node import StateNode
from stateman.utils import Validatable


class StateGraph(Validatable):
    """This contains a graph of StateNodes

    Attributes:
        graph (DiGraph): a directed graph of StateNodes that depend on each other
        nodes (Dict[str, StateNode]): path -> nodes mappings for quick lookup
        validations (List[function]): validations to be performed against this graph
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = {}
        self.validateions = []

        self.nodes['/'] = StateNode(pathh='/', name='root')
        self.graph.add_node(self.nodes['/'])

    def register_validation(self):
        pass

    def populate(self):
        raise NotImplementedError()

    def reconcile(self, expected_state, dry_run=False):
        """Reconcile's our graph to make it look like the expected_state"""
