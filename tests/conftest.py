import pytest


@pytest.fixture()
def dummy_data():
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
def server_node_cls():
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
def job_node_cls():
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

    return JobNode


@pytest.fixture()
def dummy_data_nodes(server_node_cls, job_node_cls, dummy_data):
    nodes = {}
    for key, value in dummy_data.NODES.items():
        if value['type'] == 'job':
            nodes[key] = job_node_cls(path=value['path'], **value['state'])
        elif value['type'] == 'server':
            nodes[key] = server_node_cls(path=value['path'], **value['state'])

    return nodes


@pytest.fixture()
def dummy_data_edges(dummy_data):
    return dummy_data.EDGES
