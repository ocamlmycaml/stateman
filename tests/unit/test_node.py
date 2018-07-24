from stateman.node import Node


def test_node_create_root():
    """Ensures a root node can be created"""

    node = Node(path='', name='root')
    assert node.path == ('',)
    assert node.props == {'name': 'root'}


def test_node_create_random(mock_data):
    """Ensures a node gets created"""

    test_node = mock_data.NODES['solrcloudc3']
    actual_node = Node(path=test_node['path'], **test_node['props'])
    actual_path = tuple(test_node['path'].split('/'))

    assert actual_node.path == actual_path
    assert actual_node.props == test_node['props']
