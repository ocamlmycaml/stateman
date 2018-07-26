import pytest
from tests.mockdata import api_calls, data


@pytest.fixture()
def mock_data():
    return data


@pytest.fixture()
def mock_api_calls():
    return api_calls


@pytest.fixture()
def node_cls():
    """register some transitions with a mode class and return it

    Returns:
        class: with a state transition registered to it
    """
    from stateman.node import StateNode

    class Node(StateNode):
        state = {'name': 'pre-transition'}

    return Node


@pytest.fixture()
def mock_nodes(node_cls, mock_data):
    return {
        key: node_cls(name=value['name'], **value['props'])
        for key, value in mock_data.items()
    }
