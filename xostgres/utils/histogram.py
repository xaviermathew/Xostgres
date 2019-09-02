from collections import Counter
import math
from pprint import pformat

from xostgres.utils import counter, get_chunksize, pairwise, bin_values, to_dict


class BaseHistogram(object):
    def __init__(self, max_keys):
        self.max_keys = max_keys
        self.data = Counter()

    def __repr__(self):
        return '<%s\n%s>' % (self.__class__.__name__, pformat(to_dict(self.data)))

    def get_hist_key(self, value, for_predicting=False):
        hist = self.data
        hist_keys = sorted(hist.keys())
        if not for_predicting:
            if not hist_keys or len(hist_keys) < self.max_keys:
                return value
            elif value < hist_keys[0]:
                hist[value] = hist.pop(hist_keys[0])
                return value
        for hk1, hk2 in pairwise(hist_keys):
            if hk1 <= value < hk2:
                return hk1
        return hist_keys[-1]

    def get_count(self, value):
        hist_key = self.get_hist_key(value, for_predicting=True)
        return self.data[hist_key]['total']

    def fit(self, values):
        raise NotImplementedError

    def fit_one(self, value):
        raise NotImplementedError


class DynamicHistogram(BaseHistogram):
    def fit_one(self, value):
        hist_key = self.get_hist_key(value)
        self.data[hist_key] += 1


class FixedWidthHistogram(BaseHistogram):
    def fit(self, values):
        total = len(values)
        max_chunks = min(total, self.max_keys)
        chunksize = get_chunksize(values, max_chunks)
        idx_set = range(0, total, chunksize)
        hist = {}
        for i, idx in enumerate(idx_set):
            if (i + 1) == len(idx_set):
                n = (total % chunksize) or chunksize
            else:
                n = chunksize
            hist[values[idx]] = n
        self.data.clear()
        self.data.update(hist)

    def get_bin_width(self, table, column, value):
        # use UniqueStore if not overflown
        total = table.stat.stat_store.data[table.name]['total']
        bin_width = int(math.ceil(float(total) / self.max_keys))
        hist_key = self.get_hist_key(value, for_predicting=True)
        num_entries = self.data[table.name][column][hist_key]
        return min(num_entries, bin_width)


class VariableWidthHistogram(BaseHistogram):
    def fit(self, values):
        freq_map = dict(counter(values))
        c = bin_values(values, freq_map, self.max_keys)
        hist = {v_set[0]: {'total': sum([freq_map[v] for v in v_set]),
                           'num_uniques': len(v_set)}
                for v_set in c}
        self.data.clear()
        self.data.update(hist)

    def get_bin_width(self, table, column, value):
        hist_key = self.get_hist_key(value, for_predicting=True)
        return self.data[hist_key]['num_uniques']
