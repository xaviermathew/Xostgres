from pprint import pformat

from xostgres.utils import to_dict, defaultdict
from xostgres.utils.histogram import DynamicHistogram, FixedWidthHistogram, \
    VariableWidthHistogram


class BaseStat(object):
    def __init__(self):
        self.data = {}

    def __repr__(self):
        return '<%s\n%s>' % (self.__class__.__name__, pformat(to_dict(self.data)))

    def add_entry(self, table, d):
        raise NotImplementedError


class UniqueStore(BaseStat):
    max_values = 100

    def add_entry(self, table, d):
        if table.name in self.data:
            uniques = self.data[table.name]
        else:
            uniques = self.data[table.name] = defaultdict(lambda: {'uniques': set(), 'overflow': False})
        for column, value in d.items():
            if len(uniques[column]['uniques']) < self.max_values:
                uniques[column]['uniques'].add(value)
                if len(uniques[column]['uniques']) >= self.max_values:
                    uniques[column]['overflow'] = True


class StatStore(BaseStat):
    def add_entry(self, table, d):
        if table.name in self.data:
            stats = self.data[table.name]
        else:
            stats = self.data[table.name] = {'columns': defaultdict(lambda: {'min': None, 'max': None}),
                                             'total': None}

        if stats['total'] is None:
            stats['total'] = 1
        stats['total'] += 1

        for column, value in d.items():
            if stats['columns'][column]['min'] is None:
                stats['columns'][column]['min'] = stats['columns'][column]['max'] = value
            else:
                stats['columns'][column]['min'] = min(stats['columns'][column]['min'], value)
                stats['columns'][column]['max'] = max(stats['columns'][column]['max'], value)


class HistogramStore(BaseStat):
    max_keys = 10

    def add_entry(self, table, d):
        if table.name in self.data:
            hist = self.data[table.name]
        else:
            hist = self.data[table.name] = defaultdict(lambda: DynamicHistogram(self.max_keys))
        for column, value in d.items():
            hist[column].fit_one(value)

    def _recalculate(self, table, column):
        values = sorted([d[column] for d in table.data])
        total = table.stat.stat_store.data[table.name]['total']
        num_uniques = len(table.stat.unique_store.data[table.name][column]['uniques'])
        percent_uniques = float(num_uniques) / total
        overflown = table.stat.unique_store.data[table.name][column]['overflow']
        if True or (not overflown and percent_uniques <= 0.3):
            hist_class = VariableWidthHistogram
        else:
            hist_class = FixedWidthHistogram
        print 'hist_class:%s - total:%s num_uniques:%s percent_uniques:%s overflown:%s' % (
            hist_class, total, num_uniques, percent_uniques, overflown
        )
        hist = hist_class(self.max_keys)
        hist.fit(values)
        return hist

    def recalculate(self, table, column):
        self.data[table.name][column] = self._recalculate(table, column)


class Stat(object):
    def __init__(self):
        self.unique_store = UniqueStore()
        self.stat_store = StatStore()
        self.hist_store = HistogramStore()

    def add_entry(self, table, d):
        self.unique_store.add_entry(table, d)
        self.stat_store.add_entry(table, d)
        self.hist_store.add_entry(table, d)


STAT = Stat()
