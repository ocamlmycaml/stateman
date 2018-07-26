import pytest

from stateman.node import StateNode, global_transition_functions


@pytest.fixture()
def node_with_transitions():
    """register some transitions with a mode class and return it

    Returns:
        class: with a state transition registered to it
    """
    global runcounter
    runcounter = 0

    class NodeWithTransitions(StateNode):
        state = {'name': 'pre-transition'}

    @NodeWithTransitions.register_transition(
        name='post-transition',
        something_else='something'
    )
    def transition(node):
        global runcounter
        runcounter += 1

    @NodeWithTransitions.register_transition(
        name='post-transition',
        something_else=None
    )
    def transition_again(node):
        global runcounter
        runcounter += 1

    yield NodeWithTransitions, transition, transition_again

    # clean up that global
    del runcounter


def test_node_create_root():
    """Ensures a root node can be created"""

    node = StateNode(path='/', name='root')
    assert node.path == ('',)
    assert node.path_string == '/'
    assert node.state == {'name': 'root'}


def test_node_create_with_state_data(mock_data):
    """Ensures a node gets created"""

    test_node = mock_data.NODES['extract.skyloft_us']
    actual_node = StateNode(path=test_node['path'], **test_node['state'])
    actual_path = tuple(test_node['path'][1:].split('/'))

    assert actual_node.path == actual_path
    assert actual_node.path_string == test_node['path']
    assert actual_node.state == test_node['state']


def test_node_class_create_func():
    """Ensure's create function works as expected when state is defined"""
    empty = StateNode.create('/')
    assert empty.state == {}

    class RootNode(StateNode):
        state = {'name': 'root'}

    root = RootNode.create('/')
    assert root.state == {'name': 'root'}

    extra_root = RootNode.create('/', started=True)
    assert extra_root.state == {'name': 'root', 'started': True}


def test_node_class_register_wrapper(node_with_transitions):
    """StateNodes register transitions and the transitions need to happen after they run"""
    NodeWithTransitions, transition, transition_again = node_with_transitions

    # ensure function made it to global transitions map
    state_key = (('name', 'post-transition'), ('something_else', 'something'))
    assert NodeWithTransitions in global_transition_functions
    assert state_key in global_transition_functions[NodeWithTransitions]


def test_node_class_performs_transition(node_with_transitions):
    NodeWithTransitions, transition, transition_again = node_with_transitions

    # now check if the transitioning logic works
    node = NodeWithTransitions.create('/')
    before_run = runcounter
    assert node.state == {'name': 'pre-transition'}

    transition(node)
    assert node.state == {'name': 'post-transition', 'something_else': 'something'}
    assert runcounter == before_run + 1

    transition_again(node)
    assert node.state == {'name': 'post-transition'}
    assert runcounter == before_run + 2


def test_node_transition_functions_accept_only_one_class(node_with_transitions):
    NodeWithTransitions, transition, transition_again = node_with_transitions

    # check to make sure an assertion is raised if I use a different StateNode class,
    # or a different childclass of StateNode
    with pytest.raises(ValueError):
        transition(StateNode.create('/'))

    class RootNode(StateNode):
        state = {'name': 'root'}

    with pytest.raises(ValueError):
        transition(RootNode.create('/'))
