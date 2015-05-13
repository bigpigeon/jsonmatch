if __name__ == '__main__':
    import sys
    import os

    sys.path.append(os.path.realpath('.'))

from jsonmatch.single import filter_with_single
from jsonmatch.multiple import filter_with_multiple
from jsonmatch.error import MatchError


def t1():
    rule = {'a.*.c': 20}
    data = {'a':
                {
                    'b1': {'c': 20},
                    'b2': {'c': 30}
                }
    }
    print filter_with_single(rule, data)


def t2():
    rule = {'a.*.c': {'max': 100, 'min': 50}}
    data = {'a':
                {
                    'b1': {'c': 30},
                    'b2': {'c': 60},
                    'b3': {'c': 110}
                }
    }
    print filter_with_single(rule, data)


def t3():
    rule = {'a.[].c': 30}
    data = {'a':
                {
                    'b1': {'c': 30},
                    'b2': {'c': 60},
                    'b3': {'c': 110}
                }
    }
    try:
        print filter_with_single(rule, data)
    except MatchError, what:
        print what
    rule = {'*.?[].c': 30}
    print filter_with_single(rule, data)


def t4():
    rule = {'a.{}.c': {'key': 'C'}, 'a.*.d': {'key': 'D'}}
    formula = {'D0 - C0': {'max': 30}}
    data = {'a':
                {
                    'b1': {'c': 30, 'd': 40},
                    'b2': {'c': 60, 'd': 80},
                    'b3': {'c': 90, 'd': 140}
                }
    }
    print filter_with_multiple(rule, formula, {}, data)


def t5():
    rule = {'a.{}.c': {'key': 'C'}, 'a.{}.d': {'key': 'D'}}
    formula = {'(C0-C1-C2)*(D0-D1-D2)': {'max': 500}}
    data0 = {'a':
                 {
                     'b1': {'c': 50, 'd': 40},
                     'b2': {'c': 100, 'd': 90},
                     'b3': {'c': 70, 'd': 15},
                     'b4': {'c': 199, 'd': 558}
                 }
    }

    data1 = {'a':
                 {
                     'b1': {'c': 40, 'd': 30},
                     'b2': {'c': 50, 'd': 30},
                     'b3': {'c': 60, 'd': 10},
                 }
    }

    data2 = {'a':
                 {
                     'b1': {'c': 5, 'd': 5},
                     'b2': {'c': 5, 'd': 5},
                     'b3': {'c': 5, 'd': 10},
                 }
    }
    print filter_with_multiple(rule, formula, {}, data0, data1, data2)


def t6():
    rule = {'world.islands.[].resource': {'key': 'R'}}
    formula = {'R0-R1': {'max': 500}}
    list_group_rule = {'world.islands.[]': ['id']}
    data0 = {
        'world': {
            'islands': [
                {'id': '001', 'resource': 900000},
                {'id': '002', 'resource': 500045},
                {'id': '003', 'resource': 987112}

            ]
        },
        'datetime': '2015-5-12 17:22:12'
    }
    data1 = {
        'world': {
            'islands': [
                {'id': '001', 'resource': 890000},
                {'id': '002', 'resource': 500000},
                {'id': '003', 'resource': 300000}

            ]
        },
        'datetime': '2015-5-12 17:21:00'
    }
    print filter_with_multiple(rule, formula, list_group_rule, data0, data1)

t6()