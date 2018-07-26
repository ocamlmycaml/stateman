NODES = {
    'root': {
        'path': '/',
        'state': {
            'name': 'root'
        }
    },
    'javaadmin01': {
        'path': '/javaadmin01',
        'state': {
            'type': 'host',
            'datacenter': 'bo1',
            'status': 'up'
        }
    },
    'javaadmin02': {
        'path': '/javaadmin02',
        'state': {
            'type': 'host',
            'datacenter': 'bo1',
            'status': 'down'
        }
    },
    'extract.skyloft_us': {
        'path': '/javaadmin01/extract.skyloft_us',
        'state': {
            'type': 'job',
            'job_type': 'extract',
            'collection': 'skyloft_us',
            'bclgid': 1
        }
    },
    'publish.skyloft_us.solrcloudc3': {
        'path': '/javaadmin01/publish.skyloft_us.solrcloudc4',
        'state': {
            'type': 'job',
            'job_type': 'publish',
            'collection': 'skyloft_us',
            'target': 'solrcloudc3',
            'bclgid': 1
        }
    },
    'publish.skyloft_us.solrcloudc4': {
        'path': '/javaadmin01/publish.skyloft_us.solrcloudc4',
        'state': {
            'type': 'job',
            'job_type': 'publish',
            'collection': 'skyloft_us',
            'target': 'solrcloudc4',
            'bclgid': 1
        }
    },
}

EDGES = [
    (NODES['root'], NODES['javaadmin01']),
    (NODES['root'], NODES['javaadmin02']),
    (NODES['javaadmin01'], NODES['extract.skyloft_us']),
    (NODES['javaadmin01'], NODES['publish.skyloft_us.solrcloudc3']),
    (NODES['javaadmin01'], NODES['publish.skyloft_us.solrcloudc4']),
]
