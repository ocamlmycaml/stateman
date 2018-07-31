import pytest

from stateman.node import StateNode
from stateman.utils import ValidationError


@pytest.fixture()
def transition_node_cls(node_cls):
    @node_cls.register_transition(
        from_={
            'name': 'pre-transition'
        },
        to={
            'name': 'post-transition',
            'something_else': 'something'
        }
    )
    def transition(node):
        pass

    @node_cls.register_transition(
        from_={
            'something_else': 'something'
        },
        to={
            'something_else': None
        }
    )
    def transition_again(node):
        pass

    @node_cls.register_transition(
        from_={
            'name': 'post-transition'
        },
        to={
            'blah': 'blah'
        }
    )
    def transition_a_third_time(node):
        pass

    @node_cls.register_transition(
        from_={
            'name': 'pre-transition'
        },
        to={
            'name': 'post-transition',
            'blah': 'blah'
        }
    )
    def alternative_transition(node):
        pass

    return node_cls


def test_node_create_root():
    """Ensures a root node can be created"""
    node = StateNode(path='/', name='root')
    assert node.path == ('',)
    assert node.path_string == '/'
    assert node.state == {'name': 'root'}


def test_node_create_with_state_data(mock_data):
    """Ensures a node gets created"""

    test_node = mock_data.NODES['extract.tweets']
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


def _validate_neighbors(node, expected_neighbor_states):
    neighbors = node.get_transitions_and_neighbors()
    for neighbor in neighbors.values():
        assert neighbor.path == node.path

    neighbor_states = {key: value.state for key, value in neighbors.items()}
    assert neighbor_states == expected_neighbor_states


def test_node_finds_next_transitions(transition_node_cls):
    node = transition_node_cls.create('/sample/node')
    _validate_neighbors(node, {
        (('name', 'post-transition'), ('something_else', 'something')): {
            'name': 'post-transition',
            'something_else': 'something'
        },
        (('blah', 'blah'), ('name', 'post-transition')): {
            'name': 'post-transition',
            'blah': 'blah'
        }
    })

    # identifies transitions in different states as well
    node = transition_node_cls.create('/sample/node2', name='post-transition', something_else='something')
    _validate_neighbors(node, {
        (('something_else', None),): {
            'name': 'post-transition'
        },
        (('blah', 'blah'),): {
            'name': 'post-transition',
            'something_else': 'something',
            'blah': 'blah'
        }
    })

    # doesn't lose extra state info
    node = transition_node_cls.create('/sample/node3', cat='leopard')
    _validate_neighbors(node, {
        (('name', 'post-transition'), ('something_else', 'something')): {
            'name': 'post-transition',
            'something_else': 'something',
            'cat': 'leopard'
        },
        (('blah', 'blah'), ('name', 'post-transition')): {
            'name': 'post-transition',
            'blah': 'blah',
            'cat': 'leopard'
        }
    })


def test_node_respects_validations(transition_node_cls):

    @transition_node_cls.register_validation
    def mock_validate(node):
        if 'something_else' in node.state and node.state['something_else'] == 'something':
            raise ValidationError()

    # only the blah/blah state should be present:
    node = transition_node_cls.create(path='/node/for/test')
    _validate_neighbors(node, {
        (('blah', 'blah'), ('name', 'post-transition'),): {
            'name': 'post-transition',
            'blah': 'blah'
        }
    })

    # if already in an invalid state, we should be able to transition out of it
    node = transition_node_cls.create(path='/node/for/test/2', something_else='something')
    _validate_neighbors(node, {
        (('something_else', None),): {
            'name': 'pre-transition'
        }
    })
