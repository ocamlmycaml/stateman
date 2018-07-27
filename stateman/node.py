from stateman.utils import Transitionable, Validatable, \
    global_transition_functions, global_validation_functions, ValidationError


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

    def get_transitions_and_neighbors(self):
        """Gets the next possible transitions for this particular node

        Returns:
            Dict: mapping possible transitions to neighbors of this node
        """
        possible_transitions = global_transition_functions.get(self.__class__, {})
        validations = global_validation_functions.get(self.__class__, [])
        current_state = tuple(sorted(self.state.items()))
        neighbors = {}

        for from_state_props, transitions in possible_transitions.items():
            if all((item in current_state) for item in from_state_props):
                for transition in transitions:
                    # who we tryna be
                    neighbor_state = {**self.state, **dict(transition)}
                    neighbor_state = {key: value for key, value in neighbor_state.items() if value is not None}
                    neighbor = self.create(self.path_string, **neighbor_state)

                    # make sure we can go there
                    valid = True
                    for validation_func in validations:
                        try:
                            validation_func(neighbor)
                        except ValidationError as e:
                            valid = False
                            break

                    if valid:
                        neighbors[transition] = neighbor

        return neighbors
