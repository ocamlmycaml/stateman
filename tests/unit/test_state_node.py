import pytest

from stateman.node import StateNode
from stateman.utils import global_transition_functions, global_validation_functions


@pytest.fixture()
def node_cls():
    """register some transitions with a mode class and return it

    Returns:
        class: with a state transition registered to it
    """
    class Node(StateNode):
        state = {'name': 'pre-transition'}

    return Node


@pytest.fixture()
def transition_func(node_cls):
    global transition_func_counter
    transition_func_counter = 0

    @node_cls.register_transition(
        name='post-transition',
        something_else='something'
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
        name='post-transition',
        something_else=None
    )
    def transition_again(node):
        global transition_func2_counter
        transition_func2_counter += 1

    yield transition_again

    # clean up that global
    del transition_func2_counter


@pytest.fixture()
def validation_success_func(node_cls):
    global validation_success_counter
    validation_success_counter = 0

    @node_cls.register_validation
    def validate(node):
        global validation_success_counter
        validation_success_counter += 1

    yield validate

    # clean up that global
    del validation_success_counter


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


def test_node_class_register_wrapper(node_cls, transition_func, transition_func2):
    """StateNodes register transitions and the transitions need to happen after they run"""
    # ensure function made it to global transitions map
    state_key = (('name', 'post-transition'), ('something_else', 'something'))
    assert node_cls in global_transition_functions
    assert state_key in global_transition_functions[node_cls]


def test_node_class_performs_transition(node_cls, transition_func, transition_func2):
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


def test_node_transition_functions_accept_only_one_class(transition_func):
    # check to make sure an assertion is raised if I use a different StateNode class,
    # or a different childclass of StateNode
    with pytest.raises(ValueError):
        transition_func(StateNode.create('/'))

    class RootNode(StateNode):
        state = {'name': 'root'}

    with pytest.raises(ValueError):
        transition_func(RootNode.create('/'))


def test_node_class_validation_wrapper(node_cls, validation_success_func):
    assert node_cls in global_validation_functions
    assert len(global_validation_functions[node_cls]) == 1


def test_node_validation_functions(node_cls, validation_success_func):
    node = node_cls.create(path='/')

    global validation_success_counter
    before_call = validation_success_counter
    validation_success_func(node)
    assert validation_success_counter == before_call + 1

    @node_cls.register_validation
    def validation_fail(node):
        raise Exception("Mock failure")

    with pytest.raises(Exception):
        validation_fail(node_cls.create('/'))

    with pytest.raises(ValueError):
        validation_fail(StateNode.create('/'))


def test_node_total_validation(node_cls, validation_success_func):
    node = node_cls.create(path='/')

    global validation_success_counter
    before_call = validation_success_counter
    node.validate()
    assert validation_success_counter == before_call + 1

    @node_cls.register_validation
    def validation_fail(node):
        raise Exception("Mock failure")

    with pytest.raises(Exception):
        node.validate()
