import pytest
import mock


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


@pytest.fixture(scope="function")
def mock_state_node_cls():
    # TODO: Mock this baby
    from stateman.node import StateNode
    from stateman.utils import global_transition_functions, global_validation_functions

    # lets remove all transitions and validation functions
    keys = list(global_transition_functions.keys())
    for key in keys:
        global_transition_functions.pop(key)

    keys = list(global_validation_functions.keys())
    for key in keys:
        global_validation_functions.pop(key)

    return StateNode


@pytest.fixture(scope="function")
def state_graph_cls(mock_state_node_cls):
    from stateman.utils import global_transition_functions, global_validation_functions

    # lets remove all transitions and validation functions
    keys = list(global_transition_functions.keys())
    for key in keys:
        global_transition_functions.pop(key)

    keys = list(global_validation_functions.keys())
    for key in keys:
        global_validation_functions.pop(key)

    # lets patch statenode to use what we have fixtured:
    with mock.patch('stateman.graph.StateNode', mock_state_node_cls):
        from stateman.graph import StateGraph
        yield StateGraph
