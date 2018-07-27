import heapq

from stateman.utils import Transitionable, Validatable, global_transition_functions, global_validation_functions


class PriorityItem(object):
    def __init__(self, priority=0, item=None):
        self.priority = priority
        self.item = item

    def __lt__(self, other):
        return self.priority < other.priority


def _a_star_heuristic(state_from, state_to):
    """Since we're working with the sorted tuple representations of dictionaries, we just have to
    identify how many of the (key, value) tuples of state_from are in state_to"""
    return [(pair in state_to) for pair in state_from].count(True)


def _a_star_valid_state_transitions(
        current_state,
        desired_state,
        possible_transitions,
        validations
):
    """This function uses an A* graph search algorithm to find the minimal set of transitions to a particular
    state

    shamelessly copied from: https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar

    Args:
        current_state (Dict[str, str]): where we are
        desired_state (Dict[str, str]): where we want to be
        possible_transitions (Dict[Tuple(Tuple(str, str)), Tuple(Tuple(str, str))]): what it says
        validations (List[func]): functions to validate transition

    Yields:
        List[Tuple[Tuple[str, str]]: list of transitions
    """
    frontier = []  # priority queue of (priority, state) tuples
    heapq.heappush(frontier, PriorityItem(0, current_state))

    came_from = {}
    cost_so_far = {}
    came_from[current_state] = None
    cost_so_far[current_state] = 0

    while len(frontier) > 0:
        current = heapq.heappop(frontier).item

        # if we reached our goal, leggo
        if current == desired_state:
            states = [desired_state]
            transitions = []
            while came_from[states[-1]] is not None:
                prev, transition = came_from[states[-1]]
                states.append(prev)
                transitions.append(transition)

            yield [
                dict(transition_tuple)
                for transition_tuple in reversed(transitions)
            ]

        # identify our "neighbor" states
        neighbors = {}
        for from_state_props, transitions in possible_transitions.items():
            if all((item in current) for item in from_state_props):
                for transition in transitions:
                    # who we tryna be
                    neighbor = {**dict(current), **dict(transition)}

                    valid = True
                    for validation_func in validations:
                        try:
                            validation_func(neighbor)
                        except Exception as e:
                            valid = False
                            break

                    if valid:
                        neighbors[transition] = tuple(sorted(neighbor.items()))

        # keep doing the a-star dance
        for transition, neighbor in neighbors.items():
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + _a_star_heuristic(neighbor, desired_state)
                heapq.heappush(frontier, PriorityItem(priority, neighbor))
                came_from[neighbor] = (current, transition)


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

    def get_best_transitions_to(self, desired_state):
        """Get's transitions that make the most sense to get to the state we want to. This
        checks to make sure transitions are possible, and that each transition is a valid one.

        Args:
            desired_state (Dict[str, object]): state we want to get to

        Yields:
            Tuple[Tuple[str, object]]: state transition keys
        """
        # identify all possible state keys and transitions
        all_state_keys = set()
        transitions = {}
        for from_state, to_state_dict in global_transition_functions[self.__class__].items():
            # build a set of all possible keys in states
            all_state_keys.update(key for key, _ in from_state)
            for to_state in to_state_dict:
                all_state_keys.update(key for key, _ in to_state)

            # build a map of transitions from -> to states (ignoring mapped functions for now)
            transitions[from_state] = list(to_state_dict.keys())

        # get all validations
        validations = global_validation_functions[self.__class__]

        # create current state
        full_current_state = {key: None for key in all_state_keys}
        full_current_state.update(self.state)

        # create desired state
        full_desired_state = {**full_current_state, **desired_state}

        # let the magic happen
        yield from _a_star_valid_state_transitions(
            tuple(sorted(full_current_state.items())),
            tuple(sorted(full_desired_state.items())),
            transitions,
            validations
        )
