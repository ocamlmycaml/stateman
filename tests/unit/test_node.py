from stateman.node import Node


def test_node_create(mock_data):
    """Ensures a node gets created"""

    test_node = mock_data.NODES[0]
    actual_node = Node(name=test_node['name'], **test_node['props'])

    assert actual_node.name == test_node['name']
    assert actual_node.props == test_node['props']
