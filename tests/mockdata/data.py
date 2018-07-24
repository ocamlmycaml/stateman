NODES = {
    'root': {
        'path': '/',
        'props': {
            'name': 'root'
        }
    },
    'solrcloudc3': {
        'path': '/solrcloud/solrcloudc3',
        'props': {
            'name': 'SolrCloud C3',
            'type': 'cluster',
            'application': 'solrcloud',
            'cluster': 'C3'
        }
    },
    'solrcloudc4': {
        'path': '/solrcloud/solrcloudc4',
        'props': {
            'name': 'SolrCloud C4',
            'type': 'cluster',
            'application': 'solrcloud',
            'cluster': 'C4'
        }
    },
    'solrcloudc3n01': {
        'path': '/solrcloud/solrcloudc3/n01',
        'props': {
            'name': 'SolrCloud C3',
            'type': 'node',
            'application': 'solrcloud',
            'cluster': 'C3',
            'node': 1
        }
    },
    'solrcloudc3n02': {
        'path': '/solrcloud/solrcloudc3/n02',
        'props': {
            'name': 'SolrCloud C3',
            'type': 'cluster',
            'application': 'solrcloud',
            'cluster': 'C3',
            'node': 2
        }
    },
}

EDGES = [
    (NODES['root'], NODES['solrcloudc3']),
    (NODES['root'], NODES['solrcloudc4']),
    (NODES['solrcloudc3'], NODES['solrcloudc3n01']),
    (NODES['solrcloudc3'], NODES['solrcloudc3n02'])
]
