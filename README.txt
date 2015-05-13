============================
 README: jsonmatch
============================

usage:
1.
    rule = {'a.*.c':20}
    data = {'a':
        {
            'b1': {'c': 20},
            'b2': {'c': 30}
        }
    }
    print filter_with_single(rule, data) ->
                        [{a.*.c: 20}a.b1.c: 20]
2.
    rule = {'a.*.c': {'max':100, 'min': 50}}
    data = {'a':
        {
            'b1': {'c': 30},
            'b2': {'c': 60},
            'b3': {'c': 110}
        }
    }
    print filter_with_single(rule, data) ->
                [{a.*.c: {'max': 100, 'min': 50}}a.b2.c: 60]

3.
    rule = {'a.[].c': 30}
    data = {'a':
        {
            'b1': {'c': 30},
            'b2': {'c': 60},
            'b3': {'c': 110}
        }
    }
    print filter_with_single(rule, data) -> throw error
rewrite rule   ==>
    rule = {'a.?[].c': 30}
    filter_with_single(rule, data) -> []

4.
    rule = {'a.{}.c': {'key': 'C'}, 'a.*.d': {'key': 'D'}}
    formula = {'D0 - C0': {'max': 30}}
    data = {'a':
        {
            'b1': {'c': 30, 'd':40},
            'b2': {'c': 60, 'd': 80},
            'b3': {'c': 90, 'd': 140}
        }
    }
    print filter_with_multiple(rule, formula, {}, data) ->
                                ["source-> C0: {a.{}.c: {'key': 'C'}}a.b1.c: 30
                                 source-> D0: {a.{}.d: {'key': 'D'}}a.b1.d: 40
                                 D0 - C0: 10",
                                 "source-> C0: {a.{}.c: {'key': 'C'}}a.b2.c: 60
                                 source-> D0: {a.{}.d: {'key': 'D'}}a.b2.d: 80
                                 D0 - C0: 20"]
5.
    rule = {'a.{}.c': {'key': 'C'}, 'a.{}.d': {'key': 'D'}}
    formula = {'(C0-C1-C2)*(D0-D1-D2)': {'max': 500}}
    data0 = {'a':
        {
            'b1': {'c': 50, 'd': 40},
            'b2': {'c': 100, 'd': 90},
            'b3': {'c': 70, 'd':15},
            'b4': {'c': 199, 'd':558}
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
    print filter_with_multiple(rule, formula, {}, data0, data1, data2) ->
                                    [
                                    "C2: {a.{}.c: {'key': 'C'}}a.b1.c: 5
                                    C1: {a.{}.c: {'key': 'C'}}a.b1.c: 40
                                    C0: {a.{}.c: {'key': 'C'}}a.b1.c: 50
                                    D2: {a.{}.d: {'key': 'D'}}a.b1.d: 5
                                    D0: {a.{}.d: {'key': 'D'}}a.b1.d: 40
                                    D1: {a.{}.d: {'key': 'D'}}a.b1.d: 30
                                    (C0-C1-C2)*(D0-D1-D2): 25",
                                   "C2: {a.{}.c: {'key': 'C'}}a.b3.c: 5
                                    C1: {a.{}.c: {'key': 'C'}}a.b3.c: 60
                                    C0: {a.{}.c: {'key': 'C'}}a.b3.c: 70
                                    D2: {a.{}.d: {'key': 'D'}}a.b3.d: 10
                                    D0: {a.{}.d: {'key': 'D'}}a.b3.d: 15
                                    D1: {a.{}.d: {'key': 'D'}}a.b3.d: 10
                                    (C0-C1-C2)*(D0-D1-D2): -25"]
6.
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
    print filter_with_multiple(rule, formula, list_group_rule, data0, data1) ->
                        ["R0: {world.islands.*.resource: {'key': 'R'}}world.islands.002.resource: 500045
                        R1: {world.islands.*.resource: {'key': 'R'}}world.islands.002.resource: 500000
                        R0-R1: 45"]

analysis:
    filter_with_single(rule, dd):
    filter_with_multiple(rule, formula, list_group_rule, *dd_list):
    """
        rule -> {
            match_key: match_value
        }
        formula -> {
            eval_key: match_value
        }
            match_key -> keyword.keyword2.keyword3
                keyword -> Number or Word or '*' or '[]' or '{}' or '?' or '?[]' or '?{}'
            match_value -> Number or {pattern: value}
                pattern -> 'max' or 'min' or 'not' or 'key'
                value -> Number
            eval_key -> (num_type(Number) symbol num_type(Number))
                num_type -> 'int' or 'float'
                symbol -> all Number operators in python (+,-,*,/,%,**,...)
        dd -> {
            word_key: word_value
        }
            word_key -> prohibit: has '.' or equal to *, [], {}, ?, ?[], ?{}
            word_value -> json object

        list_group_rule -> {
            match_key: [group_key, group_key2. group_key3]
        }
            group_key -> Number or Word
        dd_list -> [dd]

    """



