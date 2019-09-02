from collections import Counter


class Sequence(object):
    def __init__(self):
        self.data = Counter()

    def __repr__(self):
        return '<Sequence %s>' % self.data

    def add_entry(self, table):
        sequence_data = table.sequence.data
        sequence_data[table.name] += 1
        return sequence_data[table.name]


SEQUENCE = Sequence()
