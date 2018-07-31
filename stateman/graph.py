import heapq

import networkx as nx

from stateman.node import StateNode
from stateman.utils import Validatable


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


class StateGraph(Validatable):
    """This contains a graph of StateNodes

    Attributes:
        graph (DiGraph): a directed graph of StateNodes that depend on each other
        nodes (Dict[str, StateNode]): path -> nodes mappings for quick lookup
        validations (List[function]): validations to be performed against this graph
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = {}

        self.root = StateNode(path='/', name='root')
        self.nodes['/'] = self.root
        self.graph.add_node(self.nodes['/'])

    def add_nodes(self, nodes):
        for node in nodes:
            assert isinstance(node, StateNode)
            assert node.path_string not in self.nodes

            self.nodes[node.path_string] = node
            self.graph.add_node(node)

    def add_edges(self, edges):
        for left, right in edges:
            self.graph.add_edge(self.nodes[left], self.nodes[right])

    def get_transitions_and_neighbors(self):
        pass

    def reconcile(self, expected_state, dry_run=False):
        """Reconcile's our graph to make it look like the expected_state"""
