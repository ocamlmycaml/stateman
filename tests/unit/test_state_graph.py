import mock

import pytest


@pytest.fixture(scope="function")
def state_node_cls():
    # TODO: Mock this baby
    from stateman.node import StateNode
    from stateman.utils import global_transition_functions, global_validation_functions

    # lets remove all transitions and validation functions
    keys = list(global_transition_functions.keys())
    for key in keys:
        global_transition_functions.pop(key)

    keys = list(global_validation_functions.keys())
    for key in keys:
        global_validation_functions.pop(key)

    return StateNode


@pytest.fixture(scope="function")
def state_graph_cls(state_node_cls):
    from stateman.utils import global_transition_functions, global_validation_functions

    # lets remove all transitions and validation functions
    keys = list(global_transition_functions.keys())
    for key in keys:
        global_transition_functions.pop(key)

    keys = list(global_validation_functions.keys())
    for key in keys:
        global_validation_functions.pop(key)

    # lets patch statenode to use what we have fixtured:
    with mock.patch('stateman.graph.StateNode', state_node_cls):
        from stateman.graph import StateGraph
        yield StateGraph


def test_create_graph(state_node_cls, state_graph_cls):
    # can i create a graph and does it have a root?
    g = state_graph_cls()
    assert '/' in g.nodes
    assert g.nodes['/'] in g.graph.nodes()

    # can I add a child?
    child = state_node_cls('/child')
    g.add_nodes([child])
    assert '/child' in g.nodes
    assert g.nodes['/child'] == child
    assert child in g.graph.nodes()

    # can i connect the child to the root?
    g.add_edges([('/', '/child')])
    assert (g.nodes['/'], child) in g.graph.edges()


def test_get_neighbor_state_graphs_is_noop(state_graph_cls):
    # no transitions == no neighbors
    sg = state_graph_cls()
    assert sg.get_transitions_and_neighbors() == {}


def test_single_node_state_graph_transitions(state_node_cls, state_graph_cls):
    # create a graph and a transition for it
    @state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        pass

    # get you some transitions
    sg = state_graph_cls()
    transitions = sg.get_transitions_and_neighbors()

    # we only have one node so it should have only that one particular possibility
    assert len(transitions) == 1
    assert ('/', (('blah', 'blah'),)) in transitions  # the thing we registered above

    # check to make sure the neighbor has the transition applied to the correct node
    neighbor = transitions[('/', (('blah', 'blah'),))]
    assert neighbor.nodes['/'].path_string == '/'
    assert neighbor.nodes['/'].state == {'name': 'root', 'blah': 'blah'}


def test_unconnected_state_graph_transitions(state_node_cls, state_graph_cls):
    # create a graph and a transition for it
    @state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        pass

    # get you some transitions, with graph containing 2 nodes and no connections
    sg = state_graph_cls()
    sg.add_nodes([state_node_cls(path='/child', name='child')])
    transitions = sg.get_transitions_and_neighbors()
    assert len(transitions) == 2
    assert ('/', (('blah', 'blah'),)) in transitions
    assert ('/child', (('blah', 'blah'),)) in transitions

    neighbor_root = transitions[('/', (('blah', 'blah'),))]
    assert neighbor_root.nodes['/'].path_string == '/'
    assert neighbor_root.nodes['/child'].path_string == '/child'
    assert neighbor_root.nodes['/'].state == {'name': 'root', 'blah': 'blah'}  # root node transitioned
    assert neighbor_root.nodes['/child'].state == {'name': 'child'}

    neighbor_child = transitions[('/child', (('blah', 'blah'),))]
    assert neighbor_child.nodes['/'].path_string == '/'
    assert neighbor_child.nodes['/child'].path_string == '/child'
    assert neighbor_child.nodes['/'].state == {'name': 'root'}
    assert neighbor_child.nodes['/child'].state == {'name': 'child', 'blah': 'blah'}  # child node transitioned

    # check that edges are correct
    assert list(neighbor_root.graph.edges()) == []
    assert list(neighbor_child.graph.edges()) == []


def test_connected_state_graph_transitions_noop(state_node_cls, state_graph_cls):
    # no transitions == no neighbors, with graph containing 2 nodes and one connection
    sg = state_graph_cls()
    sg.add_nodes([state_node_cls(path='/child', name='child')])
    sg.add_edges([('/', '/child')])
    assert sg.get_transitions_and_neighbors() == {}


def test_connected_state_graph_transitions(state_node_cls, state_graph_cls):
    # create a graph and a transition for it
    @state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        pass

    # get you some transitions, with graph containing 2 nodes and one connection between
    sg = state_graph_cls()
    sg.add_nodes([state_node_cls(path='/child', name='child')])
    sg.add_edges([('/', '/child')])
    transitions = sg.get_transitions_and_neighbors()
    assert len(transitions) == 2
    assert ('/', (('blah', 'blah'),)) in transitions
    assert ('/child', (('blah', 'blah'),)) in transitions

    neighbor_root = transitions[('/', (('blah', 'blah'),))]
    assert neighbor_root.nodes['/'].path_string == '/'
    assert neighbor_root.nodes['/child'].path_string == '/child'
    assert neighbor_root.nodes['/'].state == {'name': 'root', 'blah': 'blah'}  # root node transitioned
    assert neighbor_root.nodes['/child'].state == {'name': 'child'}

    neighbor_child = transitions[('/child', (('blah', 'blah'),))]
    assert neighbor_child.nodes['/'].path_string == '/'
    assert neighbor_child.nodes['/child'].path_string == '/child'
    assert neighbor_child.nodes['/'].state == {'name': 'root'}
    assert neighbor_child.nodes['/child'].state == {'name': 'child', 'blah': 'blah'}  # child node transitioned

    # check that edges are correct
    assert list(neighbor_root.graph.edges()) == [(neighbor_root.nodes['/'], neighbor_root.nodes['/child'])]
    assert list(neighbor_child.graph.edges()) == [(neighbor_child.nodes['/'], neighbor_child.nodes['/child'])]
