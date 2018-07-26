import networkx as nx

from stateman.node import StateNode


class StateGraph(object):
    """This contains a graph of StateNodes

    Attributes:
        graph (DiGraph): a directed graph of StateNodes that depend on each other
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.graph.add_node(StateNode(path='/', name='root'))

    def populate(self):
        raise NotImplementedError()

    def reconcile(self, expected_state, dry_run=False):
        """Reconcile's our graph to make it look like the expected_state"""
