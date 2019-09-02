import math

from xostgres.indexes import INDEX
from xostgres.sequences import SEQUENCE
from xostgres.stats import STAT


class Table(object):
    def __init__(self, name, indexed_columns=[]):
        self.name = name
        self.indexed_columns = indexed_columns
        self.data = []
        self.index = INDEX
        self.stat = STAT
        self.sequence = SEQUENCE

    def __repr__(self):
        return '<Table %s>' % self.name

    def create(self, d):
        d['id'] = self.sequence.add_entry(self)
        self.data.append(d)
        self.stat.add_entry(self, d)
        for column in self.indexed_columns:
            self.index.add_entry(self, d['id'], column, d[column])

    def predict_num_results(self, **filters):
        totals = []
        hist_map = self.stat.hist_store.data[self.name]
        for column, value in filters.items():
            hist_store = hist_map[column]
            num_entries = hist_store.get_count(value)
            bin_width = hist_store.get_bin_width(self, column, value)
            expected_total = int(math.ceil(float(num_entries) / bin_width))
            print 'col:%s value:%s num_entries:%s bin_width:%s expected_total:%s' % \
                  (column, value, num_entries, bin_width, expected_total)
            totals.append(expected_total)

        total = self.stat.stat_store.data[self.name]['total']
        probabilities = [float(t) / total for t in totals]
        total_probability = reduce(lambda x, y: x * y, probabilities)
        print 'total:%s totals:%s total_probability:%s' % \
              (total, totals, total_probability)
        return int(math.ceil(total * total_probability))

    def filter(self, **filters):
        def check(d):
            for k, v in filters.items():
                if d[k] != v:
                    return False
            return True
        return filter(check, self.data)

    def delete(self, id):
        d = self.filter(id=id)[0]
        self.data.remove(d)
