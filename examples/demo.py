from stateman.node import StateNode
from stateman.graph import StateGraph
from stateman.utils import ValidationError


def run_demo():
    print('''
    Let\'s try something cool. You\'re mining facebook for commens and likes in a certain
    ETL pipeline. As a result, you have two "extract" processes that read likes and
    comments, and a "transform" process that depends on the "extract" jobs to be running.
    All three of these are running on AWS and you'd like them to be in the same availability
    zone if you can help it.
    ''')
    nodes = [{
        'path': '/extract/likes',
        'state': {
            'running': True,
            'location': 'America/East'
        }
    }, {
        'path': '/extract/comments',
        'state': {
            'running': True,
            'location': 'America/East'
        }
    }, {
        'path': '/transform',
        'state': {
            'running': True,
            'location': 'America/East'
        }
    }]

    for node in nodes:
        print('--', node['path'], node['state'])

    print('''
    Each of those nodes are running. Let's say we have some functions that call web APIs
    and does complicated things to stop a node from running. For simplicity's sake,
    let's assume it's the same logic that does the job for all those nodes:
        class: ETLNode
        transition functions:
            start_job() -> changes the 'running' state from False to True
            stop_job() -> changes the 'running' state from True to False
            move_to_cali() -> sets the job to run in west coast
            move_to_boston() -> sets the job to run in east coast
    ''')
    input('<Press a key to continue>')

    class ETLNode(StateNode):
        pass

    @ETLNode.register_transition(from_={
        'running': False
    }, to={
        'running': True
    })
    def start_job(node):
        '''Complicated logic goes here. For now, let's let it be'''

    @ETLNode.register_transition(from_={
        'running': True
    }, to={
        'running': False
    })
    def stop_job(node):
        '''Many other complicated logics go here'''

    @ETLNode.register_transition(from_={
        'running': False,
        'location': 'America/East'
    }, to={
        'location': 'America/West'
    })
    def move_to_cali():
        '''This moves it to california'''

    print('''
    Now lets specify a validation on the graph. Transform can't run if any of the extracts are not running.
    Let's encode that into a function
        class: ETLGraph
        validation functions:
            extract_runs_when_transform_runs() -> ensures extract jobs are running when transform is running
    ''')
    input('<Press a key to continue>')

    class ETLGraph(StateGraph):
        pass

    @ETLGraph.register_validation
    def extract_runs_when_transform_runs(graph):
        if graph.nodes['/transform'].state['running'] and not (
            graph.nodes['/extract/likes'].state['running'] and graph.nodes['/extract/comments'].state['running']
        ):
            raise ValidationError("extract jobs have to be running when transform is running")

    print('''
    Phew! We did it! Now let's make a graph with our current state of affairs. All jobs running in America/East
    ''')
    input('<Press a key to continue>')

    current = ETLGraph()
    current.add_nodes([
        ETLNode(path=node['path'], **node['state'])
        for node in nodes
    ])

    print('''
    Now let's make a graph of expected state. This will be all nodes running in west coast
    ''')
    input('<Press a key to continue>')

    expected = ETLGraph()
    expected.add_nodes([
        ETLNode(path=node['path'], **{**node['state'], 'location': 'America/West'})
        for node in nodes
    ])

    print('''
    This is the magical moment. We can tell the 'current' graph to reconcile itself
    using the transitions we provided to get to the expected state. Note that it
    turns off the transform job before the extract jobs, and that the movement to west
    coast happens only when all jobs are off. Then the jobs are started extract first
    so transform won't complain
    ''')
    input('<Press a key to continue>')

    steps = current.take_shortest_path_to(expected, dry_run=True)
    for step in steps:
        print('--', step['node'], "goes from", step['from_state'], "to", step['to_state'])
