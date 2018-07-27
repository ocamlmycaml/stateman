from stateman.graph import StateGraph
from stateman.node import StateNode


def test_create_graph():
    g = StateGraph()
    assert '/' in g.nodes
    assert g.root in g.graph.nodes()

    child = StateNode('/child')
    g.add_nodes([child])
    assert '/child' in g.nodes
    assert g.nodes['/child'] == child
    assert child in g.graph.nodes()

    g.add_edges([('/', '/child')])
    assert (g.root, child) in g.graph.edges()


def test_get_neighbor_state_graphs(mock_nodes, mock_edges):

    class SiphonState(StateGraph):
        pass

    sg = StateGraph()
    sg.add_nodes(mock_nodes.values())
    sg.add_edges(mock_edges)

