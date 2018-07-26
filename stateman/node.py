from stateman.utils import Transitionable, Validatable, global_transition_functions


class StateNode(Transitionable, Validatable):
    """Represents the state of an individual piece of a system

    Attributes:
        path (Tuple[String]): identifier of node
        state (Dict[str, object]): state of the node
    """
    path = tuple()
    state = {}

    @classmethod
    def create(cls, path, **extra_state):
        """Defines how to create self. By default, this just makes an instance of the calling class

        Args:
            path (str): path identifier of node
            extra_state (Dict[str, objec]): state of node

        """
        state = {**cls.state, **extra_state}
        return cls(path, **state)

    def __init__(self, path, **state):
        assert path[0] == '/'
        self.path = tuple(path[1:].split('/'))
        self.state = state

    @property
    def path_string(self):
        return '/' + '/'.join(self.path)

    def destroy(self):
        """Defines how to destroy self"""
