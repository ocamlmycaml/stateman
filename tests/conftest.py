import pytest


@pytest.fixture()
def mock_data():
    from tests.mockdata import data
    return data


@pytest.fixture()
def node_cls():
    """register some transitions with a mode class and return it

    Returns:
        class: of type StateNode
    """
    from stateman.node import StateNode

    class Node(StateNode):
        state = {'name': 'pre-transition'}

    return Node


@pytest.fixture()
def mock_server_node_cls():
    """A node to represent a server

    Returns:
        class: what it says above
    """
    from stateman.node import StateNode

    class ServerNode(StateNode):
        state = {
            'status': 'up'
        }

    return ServerNode


@pytest.fixture()
def mock_job_node_cls():
    """A node class to represent a job

    Returns:
        class: with state transitions registered to it
    """
    from stateman.node import StateNode

    class JobNode(StateNode):
        state = {
            'status': 'stopped'
        }

    @JobNode.register_transition(
        from_={
            'status': 'stopped'
        },
        to={
            'status': 'running'
        }
    )
    def start_job(node):
        pass

    def stop_job(node):
        pass

    JobNode.register_transition(from_={'status': 'running'}, to={'status': 'stopped'})(stop_job)
    JobNode.register_transition(from_={'status': 'broken'}, to={'status': 'stopped'})(stop_job)


@pytest.fixture()
def mock_transitionable_nodes(mock_server_node_cls, mock_job_node_cls, mock_data):
    nodes = {}
    for key, value in mock_data.NODES.items():
        if value['type'] == 'job':
            nodes[key] = mock_job_node_cls(path=value['path'], **value['state'])
        elif value['type'] == 'server':
            nodes[key] = mock_server_node_cls(path=value['path'], **value['state'])

    return nodes


@pytest.fixture()
def mock_edges(mock_data):
    return mock_data.EDGES
