from typing import Type


Path = Type(tuple)


class Node(object):

    path = Path('')
    props = {}

    def __init__(self, path: Path, **props):
        self.path = path
        self.props = props
