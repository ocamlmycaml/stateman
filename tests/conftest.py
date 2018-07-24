import pytest
from tests.mockdata import api_calls, data


@pytest.fixture()
def mock_data():
    return data


@pytest.fixture()
def mock_api_calls():
    return api_calls


@pytest.fixture()
def mock_nodes(mock_data):
    from stateman.node import Node

    return {
        key: Node(name=value['name'], **value['props'])
        for key, value in mock_data.items()
    }
