import pytest

from stateman.utils import ValidationError


def test_create_graph(mock_state_node_cls, state_graph_cls):
    # can i create a graph and does it have a root?
    g = state_graph_cls()
    assert '/' in g.nodes
    assert g.nodes['/'] in g.graph.nodes()

    # can I add a child?
    child = mock_state_node_cls('/child')
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


def test_single_node_state_graph_transitions(mock_state_node_cls, state_graph_cls):
    # create a graph and a transition for it
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        pass

    # get you some transitions
    sg = state_graph_cls()
    transitions = sg.get_transitions_and_neighbors()

    # we only have one node so it should have only that one particular possibility
    assert len(transitions) == 1
    assert ('/', (), (('blah', 'blah'),)) in transitions  # the thing we registered above

    # check to make sure the neighbor has the transition applied to the correct node
    neighbor = transitions[('/', (), (('blah', 'blah'),))]
    assert neighbor.nodes['/'].path_string == '/'
    assert neighbor.nodes['/'].state == {'name': 'root', 'blah': 'blah'}


def test_unconnected_state_graph_transitions(mock_state_node_cls, state_graph_cls):
    # create a graph and a transition for it
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        pass

    # get you some transitions, with graph containing 2 nodes and no connections
    sg = state_graph_cls()
    sg.add_nodes([mock_state_node_cls(path='/child', name='child')])
    transitions = sg.get_transitions_and_neighbors()
    assert len(transitions) == 2
    assert ('/', (), (('blah', 'blah'),)) in transitions
    assert ('/child', (), (('blah', 'blah'),)) in transitions

    neighbor_root = transitions[('/', (), (('blah', 'blah'),))]
    assert neighbor_root.nodes['/'].path_string == '/'
    assert neighbor_root.nodes['/child'].path_string == '/child'
    assert neighbor_root.nodes['/'].state == {'name': 'root', 'blah': 'blah'}  # root node transitioned
    assert neighbor_root.nodes['/child'].state == {'name': 'child'}

    neighbor_child = transitions[('/child', (), (('blah', 'blah'),))]
    assert neighbor_child.nodes['/'].path_string == '/'
    assert neighbor_child.nodes['/child'].path_string == '/child'
    assert neighbor_child.nodes['/'].state == {'name': 'root'}
    assert neighbor_child.nodes['/child'].state == {'name': 'child', 'blah': 'blah'}  # child node transitioned

    # check that edges are correct
    assert list(neighbor_root.graph.edges()) == []
    assert list(neighbor_child.graph.edges()) == []


def test_connected_state_graph_transitions_noop(mock_state_node_cls, state_graph_cls):
    # no transitions == no neighbors, with graph containing 2 nodes and one connection
    sg = state_graph_cls()
    sg.add_nodes([mock_state_node_cls(path='/child', name='child')])
    sg.add_edges([('/', '/child')])
    assert sg.get_transitions_and_neighbors() == {}


def test_connected_state_graph_transitions(mock_state_node_cls, state_graph_cls):
    # create a graph and a transition for it
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        pass

    # get you some transitions, with graph containing 2 nodes and one connection between
    sg = state_graph_cls()
    sg.add_nodes([mock_state_node_cls(path='/child', name='child')])
    sg.add_edges([('/', '/child')])
    transitions = sg.get_transitions_and_neighbors()
    assert len(transitions) == 2
    assert ('/', (), (('blah', 'blah'),)) in transitions
    assert ('/child', (), (('blah', 'blah'),)) in transitions

    neighbor_root = transitions[('/', (), (('blah', 'blah'),))]
    assert neighbor_root.nodes['/'].path_string == '/'
    assert neighbor_root.nodes['/child'].path_string == '/child'
    assert neighbor_root.nodes['/'].state == {'name': 'root', 'blah': 'blah'}  # root node transitioned
    assert neighbor_root.nodes['/child'].state == {'name': 'child'}

    neighbor_child = transitions[('/child', (), (('blah', 'blah'),))]
    assert neighbor_child.nodes['/'].path_string == '/'
    assert neighbor_child.nodes['/child'].path_string == '/child'
    assert neighbor_child.nodes['/'].state == {'name': 'root'}
    assert neighbor_child.nodes['/child'].state == {'name': 'child', 'blah': 'blah'}  # child node transitioned

    # check that edges are correct
    assert list(neighbor_root.graph.edges()) == [(neighbor_root.nodes['/'], neighbor_root.nodes['/child'])]
    assert list(neighbor_child.graph.edges()) == [(neighbor_child.nodes['/'], neighbor_child.nodes['/child'])]


def test_state_graph_comapring(state_graph_cls, mock_state_node_cls):
    # empty graphs are equal (only root node to compare)
    lg = state_graph_cls()
    rg = state_graph_cls()
    assert lg.has_same_state(rg)

    # different states are unequal
    lg.nodes['/'].state['blah'] = 'blah'
    assert not lg.has_same_state(rg)

    # different nodes are unequal
    lg.add_nodes([mock_state_node_cls.create('/blah')])
    assert not lg.has_same_state(rg)

    # two unconnected nodes
    lg = state_graph_cls()
    rg = state_graph_cls()
    lg.add_nodes([mock_state_node_cls(path='/blah', name='blah')])
    rg.add_nodes([mock_state_node_cls(path='/blah', name='blah')])
    assert lg.has_same_state(rg)

    # different states are unequal
    lg.nodes['/blah'].state['name'] = 'blahtito'
    assert not lg.has_same_state(rg)

    # two connected nodes - edges must match
    lg = state_graph_cls()
    rg = state_graph_cls()
    lg.add_nodes([mock_state_node_cls(path='/blah', name='blah')])
    rg.add_nodes([mock_state_node_cls(path='/blah', name='blah')])
    lg.add_edges([('/', '/blah')])
    assert not lg.has_same_state(rg)
    rg.add_edges([('/', '/blah')])
    assert lg.has_same_state(rg)

    # different states are again unequal
    lg.nodes['/blah'].state['name'] = 'blahtito'
    assert not lg.has_same_state(rg)

    # different direction edges don't count for anything
    lg = state_graph_cls()
    rg = state_graph_cls()
    lg.add_nodes([mock_state_node_cls(path='/blah', name='blah')])
    rg.add_nodes([mock_state_node_cls(path='/blah', name='blah')])
    lg.add_edges([('/', '/blah')])
    rg.add_edges([('/blah', '/')])
    assert not lg.has_same_state(rg)

    # having additional left edges or right edges doesn't mean anything
    lg = state_graph_cls()
    rg = state_graph_cls()
    lg.add_nodes([
        mock_state_node_cls(path='/blah0', name='blah0'),
        mock_state_node_cls(path='/blah1', name='blah1'),
        mock_state_node_cls(path='/blah2', name='blah2')])
    rg.add_nodes([
        mock_state_node_cls(path='/blah0', name='blah0'),
        mock_state_node_cls(path='/blah1', name='blah1'),
        mock_state_node_cls(path='/blah2', name='blah2')
    ])
    lg.add_edges([('/', '/blah1')])
    rg.add_edges([('/', '/blah1'), ('/blah1', '/blah2')])  # '/blah1' has 1 more out_edge
    assert not lg.has_same_state(rg)
    lg.add_edges([('/blah0', '/'), ('/blah1', '/blah2')])  # now '/' has 1 more in_edge
    assert not lg.has_same_state(rg)


def test_graph_neighbors_validation_fails_removed(mock_state_node_cls, state_graph_cls):
    @state_graph_cls.register_validation
    def validate(graph):
        if 'blah' in graph.nodes['/'].state \
           and graph.nodes['/'].state['blah'] == 'blah':
            raise ValidationError("a root can't be 'blah'")

    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        pass

    g = state_graph_cls()
    assert g.get_transitions_and_neighbors() == {}

    g.add_nodes([mock_state_node_cls.create('/blah')])
    neighbors = g.get_transitions_and_neighbors()
    assert ('/blah', (), (('blah', 'blah'),)) in neighbors
    neighbor = neighbors[('/blah', (), (('blah', 'blah'),))]
    assert neighbor.nodes['/'].state == {'name': 'root'}
    assert neighbor.nodes['/blah'].state == {'blah': 'blah'}


def test_graph_find_shortest_path_noop(mock_state_node_cls, state_graph_cls):
    sg = state_graph_cls()
    sg2 = state_graph_cls()
    assert sg.take_shortest_path_to(sg2, dry_run=True) == []
    assert sg.take_shortest_path_to(sg2) == []


def test_graph_handles_no_possible_transitions(mock_state_node_cls, state_graph_cls):
    @mock_state_node_cls.register_transition(from_={'something': 'blah'}, to={'blah': 'blah'})
    def transition(node):
        return {'my_response': 'is to say blah'}

    sg = state_graph_cls()
    sg2 = state_graph_cls()
    sg2.nodes['/'].state['blah'] = 'blah'
    assert sg.take_shortest_path_to(sg2, dry_run=True) == []


def test_graph_only_tries_max_iter_times(mock_state_node_cls, state_graph_cls):
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        return {'my_response': 'is to say blah'}

    sg = state_graph_cls()
    sg2 = state_graph_cls()
    sg2.nodes['/'].state['blah'] = 'nonexistent state'

    with pytest.raises(Exception):
        sg.take_shortest_path_to(sg2, dry_run=True)


def test_graph_handles_exception_when_searching(mock_state_node_cls, state_graph_cls):
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        raise Exception('my_response is to say blah')

    sg = state_graph_cls()
    sg2 = state_graph_cls()
    sg2.nodes['/'].state['blah'] = 'blah'

    # exception not thrown during dry-run
    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'dry_run': True}
    }]

    # exception thrown here
    bad_result = sg.take_shortest_path_to(sg2)
    assert len(bad_result) == 1
    assert bad_result[0]['node'] == '/'
    assert bad_result[0]['from_state'] == {}
    assert bad_result[0]['to_state'] == {'blah': 'blah'}
    assert isinstance(bad_result[0]['exception'], Exception)
    assert str(bad_result[0]['exception']) == 'my_response is to say blah'


def test_graph_find_shortest_path_single_node(mock_state_node_cls, state_graph_cls):
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        return {'my_response': 'is to say blah'}

    sg = state_graph_cls()
    sg2 = state_graph_cls()
    sg2.nodes['/'].state['blah'] = 'blah'

    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'dry_run': True}
    }]
    assert sg.take_shortest_path_to(sg2) == [{
        'node': '/',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'my_response': 'is to say blah'}
    }]


def test_graph_find_shortest_path_multiple_nodes(mock_state_node_cls, state_graph_cls):
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        return {'my_response': 'is to say blah'}

    sg = state_graph_cls()
    sg.add_nodes([mock_state_node_cls(path='/child', name='child')])
    sg2 = state_graph_cls()
    sg2.add_nodes([mock_state_node_cls(path='/child', name='child')])
    sg2.nodes['/'].state['blah'] = 'blah'
    sg2.nodes['/child'].state['blah'] = 'blah'

    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/child',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'dry_run': True}
    }]
    assert sg.take_shortest_path_to(sg2) == [{
        'node': '/child',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'my_response': 'is to say blah'}
    }, {
        'node': '/',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'my_response': 'is to say blah'}
    }]


def test_graph_find_shortest_path_multiple_nodes_and_edges(mock_state_node_cls, state_graph_cls):
    @mock_state_node_cls.register_transition(from_={}, to={'blah': 'blah'})
    def transition(node):
        return {'my_response': 'is to say blah'}

    sg = state_graph_cls()
    sg.add_nodes([mock_state_node_cls(path='/child', name='child')])
    sg.add_edges([('/', '/child')])
    sg2 = state_graph_cls()
    sg2.add_nodes([mock_state_node_cls(path='/child', name='child')])
    sg2.add_edges([('/', '/child')])
    sg2.nodes['/'].state['blah'] = 'blah'
    sg2.nodes['/child'].state['blah'] = 'blah'

    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/child',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'dry_run': True}
    }]
    assert sg.take_shortest_path_to(sg2) == [{
        'node': '/child',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'my_response': 'is to say blah'}
    }, {
        'node': '/',
        'from_state': {},
        'to_state': {'blah': 'blah'},
        'execution_result': {'my_response': 'is to say blah'}
    }]


def test_state_graph_takes_multiple_steps(transition_node_cls, state_graph_cls):
    sg = state_graph_cls()
    sg.add_nodes([transition_node_cls.create('/child', name='pre-transition')])
    sg2 = state_graph_cls()
    sg2.add_nodes([transition_node_cls.create('/child', name='post-transition')])

    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/child',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': {'dry_run': True}
    }]
    assert sg.take_shortest_path_to(sg2) == [{
        'node': '/child',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': None
    }, {
        'node': '/child',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': None
    }]


def test_state_graph_prefers_shortest_route(transition_node_cls, state_graph_cls):
    sg = state_graph_cls()
    sg.add_nodes([
        transition_node_cls.create('/child1'),
        transition_node_cls.create('/child2'),
    ])
    sg2 = state_graph_cls()
    sg2.add_nodes([
        transition_node_cls.create('/child1', name='post-transition'),
        transition_node_cls.create('/child2', name='post-transition', blah='blah'),
    ])

    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/child1',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child1',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child2',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'blah': 'blah'},
        'execution_result': {'dry_run': True}
    }]
    assert sg.take_shortest_path_to(sg2) == [{
        'node': '/child1',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': None
    }, {
        'node': '/child1',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': None
    }, {
        'node': '/child2',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'blah': 'blah'},
        'execution_result': None
    }]


def test_state_graph_prefers_shortest_route_with_validations(transition_node_cls, state_graph_cls):
    sg = state_graph_cls()
    sg.add_nodes([
        transition_node_cls.create('/child1'),
        transition_node_cls.create('/child2')
    ])
    sg2 = state_graph_cls()
    sg2.add_nodes([
        transition_node_cls.create('/child1', name='post-transition'),
        transition_node_cls.create('/child2', name='post-transition')
    ])

    # The path is predictably that both nodes do pre-transition
    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/child2',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child1',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child1',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child2',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': {'dry_run': True}
    }]

    # now let's throw a wrench in the machinery and have a validation
    @state_graph_cls.register_validation
    def validate(state_graph):
        child1 = state_graph.nodes['/child1']
        child2 = state_graph.nodes['/child2']
        if 'something_else' in child1.state and child1.state['something_else'] == 'something' and \
           'something_else' in child2.state and child2.state['something_else'] == 'something':
            raise ValidationError("Both can't be in state 'something_else': 'something'")

    # now child2 will transition all the way first, before allowing child1 to
    assert sg.take_shortest_path_to(sg2, dry_run=True) == [{
        'node': '/child2',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child2',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child1',
        'from_state': {'name': 'pre-transition'},
        'to_state': {'name': 'post-transition', 'something_else': 'something'},
        'execution_result': {'dry_run': True}
    }, {
        'node': '/child1',
        'from_state': {'something_else': 'something'},
        'to_state': {'something_else': None},
        'execution_result': {'dry_run': True}
    }]
