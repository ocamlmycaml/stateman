import pytest

from stateman.node import StateNode
from stateman.utils import global_validation_functions


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