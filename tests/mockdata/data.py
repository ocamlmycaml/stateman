NODES = {
    'node01': {
        'path': '/node01',
        'type': 'server',
        'state': {
            'datacenter': 'bo1',
            'status': 'up'
        }
    },
    'node02': {
        'path': '/node02',
        'type': 'server',
        'state': {
            'datacenter': 'bo1',
            'status': 'up'
        }
    },
    'extract.tweets': {
        'path': '/extract/tweets',
        'type': 'job',
        'state': {
            'job_type': 'extract',
            'data': 'tweets',
            'status': 'stopped'
        }
    },
    'extract.likes': {
        'path': '/extract/likes',
        'type': 'job',
        'state': {
            'job_type': 'extract',
            'data': 'likes',
            'status': 'stopped'
        }
    },
    'transform.all_events': {
        'path': '/transform/all_events',
        'type': 'job',
        'state': {
            'job_type': 'transform',
            'data': 'all_events',
            'status': 'stopped'
        }
    },
    'load.all_events.postgres': {
        'path': '/load/all_events/postgres',
        'type': 'job',
        'state': {
            'job_type': 'load',
            'sink': 'postgres',
            'status': 'stopped'
        }
    },
    'load.all_events.elasticsearch': {
        'path': '/load/all_events/elasticsearch',
        'type': 'job',
        'state': {
            'job_type': 'load',
            'sink': 'elasticsearch',
            'status': 'stopped'
        }
    },
}

EDGES = [
    ('/', '/node01'),
    ('/', '/node02'),
    ('/node01', '/extract/tweets'),
    ('/node02', '/extract/likes'),
    ('/node01', '/transform/all_events'),
    ('/node02', '/load/all_events/postgres'),
    ('/node01', '/load/all_events/elasticsearch'),
]
