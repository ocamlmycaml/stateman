import heapq

import networkx as nx

from stateman.node import StateNode
from stateman.utils import Validatable, global_validation_functions, ValidationError


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

        # keep doing the a-star dance
        neighbors = current.get_transitions_and_neighbors()
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
    """

    def __init__(self, graph=None, nodes=None):
        if not graph:
            graph = nx.DiGraph()
        self.graph = graph

        if not nodes:
            nodes = {}
            nodes['/'] = StateNode(path='/', name='root')
            self.graph.add_node(nodes['/'])
        self.nodes = nodes

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
        validations = global_validation_functions.get(self.__class__, [])
        neighbors = {}

        for node in self.graph.nodes():
            # each node has a path it can take, so this graph can "transition" in the way that
            # each of the nodes does such a transition
            node_neighbors = node.get_transitions_and_neighbors()
            for node_transition, new_node in node_neighbors.items():
                new_graph = StateGraph(
                    graph=nx.DiGraph(self.graph),
                    nodes=dict(self.nodes)
                )

                # cool so we have a new node! let's populate the graph with the new node
                new_graph.nodes[new_node.path_string] = new_node
                new_graph.graph.add_node(new_node)
                new_graph.graph.add_edges_from([
                    (new_node, dest)
                    for _, dest in new_graph.graph.out_edges(node)
                ] + [
                    (source, new_node)
                    for source, _ in new_graph.graph.in_edges(node)
                ])
                new_graph.graph.remove_node(node)

                # make sure we can go there using our validations
                valid = True
                for validation_func in validations:
                    try:
                        validation_func(new_graph)
                    except ValidationError as e:
                        valid = False
                        break

                if valid:
                    # phew! now we can associate this "transtition" to the new graph
                    transition = (node.path_string, node_transition)
                    neighbors[transition] = new_graph

        return neighbors

    def reconcile(self, expected_state, dry_run=False):
        """Reconcile's our graph to make it look like the expected_state"""
