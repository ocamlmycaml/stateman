import heapq

import networkx as nx

from stateman.node import StateNode
from stateman.utils import Validatable, ValidationError, global_validation_functions, global_transition_functions


class PriorityItem(object):
    def __init__(self, priority=0, item=None):
        self.priority = priority
        self.item = item

    def __lt__(self, other):
        return self.priority < other.priority


def _a_star_heuristic(state_graph_from, state_graph_to):
    """Since we're working with a state_graph, we'd need to ensure the distances between all nodes is taken into account"""
    dist = 0
    for node_path in state_graph_from.nodes.keys():
        node_state_from = tuple(sorted(state_graph_from.nodes[node_path].state.items()))
        node_state_to = tuple(sorted(state_graph_to.nodes[node_path].state.items()))
        dist += [(pair in node_state_to) for pair in node_state_from].count(True)

    return dist


def _a_star_valid_state_transitions(
        current_state_graph,
        desired_state_graph,
        max_iterations=10000
):
    """This function uses an A* graph search algorithm to find the minimal set of transitions to a particular
    state

    shamelessly copied from: https://www.redblobgames.com/pathfinding/a-star/implementation.html#python-astar

    Args:
        current_state_graph (StateGraph): where we are
        desired_state (StateGraph): where we want to be
        max_iterations (int): maximum iterations through the graph to try

    Yields:
        List[Tuple[str, Tuple[str, str]]: list of (node_path, (..transition_to_make..))
    """
    frontier = []  # priority queue of (priority, state) tuples
    heapq.heappush(frontier, PriorityItem(0, current_state_graph))

    came_from = {}
    cost_so_far = {}
    came_from[current_state_graph] = None
    cost_so_far[current_state_graph] = 0

    iterations = 0
    while len(frontier) > 0:
        iterations += 1
        if iterations == max_iterations:
            raise Exception(f"Reached maximum number of iterations when exploring states: {max_iterations}")

        current = heapq.heappop(frontier).item

        # if we reached our goal, leggo
        if current.has_same_state(desired_state_graph):
            last_state = current
            transitions = []
            while came_from[last_state] is not None:
                prev, transition = came_from[last_state]
                last_state = prev
                transitions.append(transition)

            return list(reversed(transitions))

        # keep doing the a-star dance
        neighbors = current.get_transitions_and_neighbors()
        for transition, neighbor in neighbors.items():
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + _a_star_heuristic(neighbor, desired_state_graph)
                heapq.heappush(frontier, PriorityItem(priority, neighbor))
                came_from[neighbor] = (current, transition)

    return []


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
            for from_state, stuff in node_neighbors.items():
                for to_state, new_node in stuff.items():
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
                        transition = (node.path_string, from_state, to_state)
                        neighbors[transition] = new_graph

        return neighbors

    def take_shortest_path_to(self, expected_state_graph, dry_run=False):
        """Reconcile's our graph to make it look like the expected_state

        Args:
            expected_state_graph (StateGraph): where we want to be
            dry_run (bool): if we should execute associated functions (default: False)
        """
        # validate that the graphs have the same nodes and edges
        assert self.nodes.keys() == expected_state_graph.nodes.keys()

        transitions = _a_star_valid_state_transitions(self, expected_state_graph)

        if dry_run:
            return [
                {
                    'node': node_path,
                    'from_state': dict(from_state),
                    'to_state': dict(to_state),
                    'execution_result': {
                        'dry_run': True
                    }
                }
                for node_path, from_state, to_state in transitions
            ]

        results = []
        for node_path, from_state, to_state in transitions:
            node = self.nodes[node_path]
            transition_func = global_transition_functions[node.__class__][from_state][to_state]
            print(transition_func)
            result = {
                'node': node_path,
                'from_state': dict(from_state),
                'to_state': dict(to_state),
            }
            try:
                result['execution_result'] = transition_func(node)
            except Exception as e:
                result['exception'] = e

            results.append(result)

        return results

    def has_same_state(self, other):
        if self.nodes.keys() != other.nodes.keys():
            return False

        for node_path, node in self.nodes.items():
            if other.nodes[node_path].state != node.state:
                return False

        if [(left.path_string, right.path_string) for left, right in self.graph.in_edges()] != \
                [(left.path_string, right.path_string) for left, right in other.graph.in_edges()]:
            return False

        return True
