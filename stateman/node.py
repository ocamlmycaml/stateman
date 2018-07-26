from functools import wraps
from collections import defaultdict


global_transition_functions = defaultdict(dict)


class StateNode(object):
    """Represents the state of an individual piece of a system

    Attributes:
        path (Tuple[String]): identifier of node
        state (Dict[str, object]): state of the node
    """
    path = tuple()
    state = {}

    @classmethod
    def register_transition(cls, **new_state):

        def decorator(func):
            """This decorates the function, but also registers the function in the class's transition_functions
            dictinoary as a transition to the new state"""

            new_state_key = tuple(sorted(new_state.items()))
            global_transition_functions[cls][new_state_key] = func

            @wraps(func)
            def new_func(node_self):
                """This is the replacement method. We're gonna assume the first arg is a node, and in most
                cases self. if that's not the case, we will throw an error

                Args:
                    node_self (StateNode): node we are transitioning
                """
                if not isinstance(node_self, cls):
                    raise ValueError(f"You can only define transitions for instances of {cls.__name__}")

                # run function
                result = func(node_self)

                # update state
                state = {**node_self.state, **new_state}
                state = {key: value for key, value in state.items() if value is not None}
                node_self.state = state

                return result

            return new_func

        return decorator

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
