import pytest

from stateman.node import StateNode


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
