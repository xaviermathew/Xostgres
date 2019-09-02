from pprint import pformat

from xostgres.utils import to_dict, defaultdict


class HashIndex(object):
    def __init__(self):
        self.data = defaultdict(set)

    def __repr__(self):
        return '<HashIndex\n%s>' % pformat(to_dict(self.data))

    def add_entry(self, value, id):
        self.data[value].add(id)


class Index(object):
    def __init__(self):
        self.data = {}

    def __repr__(self):
        return '<Index\n%s>' % pformat(self.data)

    def add_entry(self, table, id, column, value):
        if table.name not in self.data:
            tdata = self.data[table.name] = defaultdict(lambda: defaultdict(HashIndex))
        else:
            tdata = self.data[table.name]
        tdata[table.name][column].add_entry(value, id)


INDEX = Index()
