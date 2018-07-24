

class Node(object):

    path = tuple()
    props = {}

    def __init__(self, path: str, **props):
        self.path = tuple(path.split('/'))
        self.props = props

    def get_path(self):
        return '/' + '/'.join(self.path)
