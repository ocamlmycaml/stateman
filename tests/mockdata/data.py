NODES = {
    'javaadmin01': {
        'path': '/javaadmin01',
        'type': 'server',
        'state': {
            'datacenter': 'bo1',
            'status': 'up'
        }
    },
    'javaadmin02': {
        'path': '/javaadmin02',
        'type': 'server',
        'state': {
            'datacenter': 'bo1',
            'status': 'down'
        }
    },
    'extract.skyloft_us': {
        'path': '/extract/skyloft_us',
        'type': 'job',
        'state': {
            'job_type': 'extract',
            'collection': 'skyloft_us',
            'status': 'stopped'
        }
    },
    'publish.skyloft_us.solrcloudc3': {
        'path': '/publish/skyloft_us/solrcloudc3',
        'type': 'job',
        'state': {
            'job_type': 'publish',
            'collection': 'skyloft_us',
            'target': 'solrcloudc3',
            'status': 'stopped'
        }
    },
    'publish.skyloft_us.solrcloudc4': {
        'path': '/publish/skyloft_us/solrcloudc4',
        'type': 'job',
        'state': {
            'job_type': 'publish',
            'collection': 'skyloft_us',
            'target': 'solrcloudc4',
            'status': 'stopped'
        }
    },
}

EDGES = [
    ('/', '/javaadmin01'),
    ('/', '/javaadmin02'),
    ('/javaadmin01', '/extract/skyloft_us'),
    ('/javaadmin01', '/publish/skyloft_us/solrcloudc3'),
    ('/javaadmin01', '/publish/skyloft_us/solrcloudc4'),
]
