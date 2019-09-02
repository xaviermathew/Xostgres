from collections import Counter, defaultdict as defaultdict_original
from itertools import tee
import math


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."

    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def to_dict(data):
    final = {}
    for k, v in data.items():
        if isinstance(v, Counter):
            final[k] = dict(v)
        elif isinstance(v, dict):
            final[k] = to_dict(v)
        else:
            final[k] = v
    return final


class defaultdict(defaultdict_original):
    __repr__ = dict.__repr__


def get_chunksize(iterable, n):
    return int(math.ceil(len(iterable)/float(n)))


def counter(values):
    # for sorted values only
    last_v = None
    count = 0
    for v in values:
        if last_v is None:
            last_v = v
            count = 1
        elif last_v == v:
            count += 1
        else:
            yield last_v, count
            last_v = v
            count = 1
    yield last_v, count


def move(v_set1, v_set2):
    import copy
    if len(v_set1) == 1:
        return v_set1, v_set2
    v_set1 = copy.deepcopy(v_set1)
    v_set2 = copy.deepcopy(v_set2)
    v = v_set1.pop()
    v_set2.insert(0, v)
    return v_set1, v_set2


def get_combinations(values, n):
    # import pdb;pdb.set_trace()
    initial = [values[:-1 * (n - 1)]] + [[v] for v in values[-1 * (n - 1):]]
    current = initial
    print initial
    combinations = [initial]
    while len(current[0]) > 1:
        for i in range(n - 1):
            v_set1 = current[i]
            v_set2 = current[i + 1]
            # if len(v_set1) == 1:
            #     break
            v_set1, v_set2 = move(v_set1, v_set2)
            c = []
            for j, v_set in enumerate(current):
                if j == i:
                    c.append(v_set1)
                elif j == i + 1:
                    c.append(v_set2)
                else:
                    c.append(v_set)
            print c
            combinations.append(c)
            current = c
    return combinations


def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)


def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss


def stddev(data, ddof=0.0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        return 0.0
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5


def score_c(freq_map, values):
    stddev_set = []
    for v_set in values:
        freqs = [freq_map[v] for v in v_set]
        s = stddev(freqs)
        stddev_set.append(s)
        # print v_set, freqs, s
    score = sum(stddev_set)
    print values, score, stddev_set
    return score


def get_uniques(values):
    seen = set()
    seen_add = seen.add
    return [v for v in values if v not in seen and (seen_add(v) or 1)]


def bin_values(values, freq_map, n):
    uniques = get_uniques(values)
    combinations = get_combinations(uniques, min(n, len(uniques)))
    best_bin = min(combinations, key=lambda c: score_c(freq_map, c))
    print 'best_bin', best_bin
    return best_bin
