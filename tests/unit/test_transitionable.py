import pytest

from stateman.node import StateNode
from stateman.utils import global_transition_functions


@pytest.fixture()
def transition_func(node_cls):
    global transition_func_counter
    transition_func_counter = 0

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
        global transition_func_counter
        transition_func_counter += 1

    yield transition

    # clean up that global
    del transition_func_counter


@pytest.fixture()
def transition_func2(node_cls):
    global transition_func2_counter
    transition_func2_counter = 0

    @node_cls.register_transition(
        from_={
            'something_else': 'something'
        },
        to={
            'something_else': None
        }
    )
    def transition_again(node):
        global transition_func2_counter
        transition_func2_counter += 1

    yield transition_again

    # clean up that global
    del transition_func2_counter


def test_node_transition_register_wrapper(node_cls, transition_func, transition_func2):
    """StateNodes register transitions and the transitions need to happen after they run"""
    # ensure function made it to global transitions map
    from_1 = (('name', 'pre-transition'),)
    from_2 = (('something_else', 'something'),)
    to_1 = (('name', 'post-transition'), ('something_else', 'something'))
    to_2 = (('something_else', None),)

    assert node_cls in global_transition_functions
    assert from_1 in global_transition_functions[node_cls]
    assert from_2 in global_transition_functions[node_cls]
    assert to_1 in global_transition_functions[node_cls][from_1]
    assert to_2 in global_transition_functions[node_cls][from_2]


def test_node_performs_transition(node_cls, transition_func, transition_func2):
    # now check if the transitioning logic works
    node = node_cls.create('/')
    global transition_func_counter
    before_run = transition_func_counter
    assert node.state == {'name': 'pre-transition'}

    transition_func(node)
    assert node.state == {'name': 'post-transition', 'something_else': 'something'}
    assert transition_func_counter == before_run + 1

    transition_func2(node)
    global transition_func2_counter
    assert node.state == {'name': 'post-transition'}
    assert transition_func2_counter == before_run + 1


def test_node_transition_functions_errors(node_cls, transition_func):
    # check to make sure an assertion is raised if I use a different StateNode class,
    # or a different childclass of StateNode
    with pytest.raises(ValueError):
        transition_func(StateNode.create('/'))

    class RootNode(StateNode):
        state = {'name': 'root'}

    with pytest.raises(ValueError):
        transition_func(RootNode.create('/'))

    node = node_cls.create('/', name='some other state')

    with pytest.raises(ValueError):
        transition_func(node)
