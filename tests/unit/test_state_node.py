import pytest

from stateman.node import StateNode


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


def test_node_finds_next_transition(transition_node_cls):
    node = transition_node_cls.create('/sample/node')

    # works if you give the exact full version of next transition
    assert list(node.get_best_transitions_to({'name': 'post-transition', 'something_else': 'something'})) ==\
        [[{'name': 'post-transition', 'something_else': 'something'}]]

    # doesn't work if you give a superset that doesn't exist
    assert list(node.get_best_transitions_to({'name': 'para-transition'})) ==\
        []


def test_node_finds_multiple_transition(transition_node_cls):
    node = transition_node_cls.create('/sample/node')

    # works to find two steps
    assert list(node.get_best_transitions_to({'name': 'post-transition'})) ==\
        [[{'name': 'post-transition', 'something_else': 'something'}, {'something_else': None}]]

    # identifies shortestt path first, but yields all others
    assert list(node.get_best_transitions_to({'name': 'post-transition', 'blah': 'blah'})) ==\
        [
            [{'name': 'post-transition', 'blah': 'blah'}],
            [{'name': 'post-transition', 'something_else': 'something'},
             {'something_else': None},
             {'blah': 'blah'}]
        ]


@pytest.mark.skip
def test_node_respects_validations(transition_node_cls):

    @transition_node_cls.register_validation
    def mock_validate(node):
        if node.state['something_else'] == 'something':
            raise ValueError()

    node = transition_node_cls.create(path='/node/for/test')
    assert list(node.get_best_transitions_to({'name': 'post-transition', 'something_else': 'something'})) ==\
        []

    assert list(node.get_best_transitions_to({'name': 'post-transition', 'blah': 'blah'})) ==\
        [
            [{'name': 'post-transition', 'blah': 'blah'}]
        ]
