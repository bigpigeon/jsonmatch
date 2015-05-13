# coding=utf-8
from jsonmatch.common import JsonNode, create_json_node_list, _create_check
from jsonmatch.error import MatchConfigError


def filter_with_single(rule, dd):
    """
    :param rule: just like: {'a.*.b':20} or {'a.d.c':{'max':40, 'min':20}}
    :param dd: data dict
    :return: a dict with out of range data
    """
    assert isinstance(rule, dict)
    assert isinstance(dd, dict)
    match = []
    for k, r in rule.iteritems():
        match += _monitor_targets_rule(k, r, dd)
    return match

#=====================================================
#            private func
#=====================================================


def _monitor_targets_rule(full_key, rule, dd):
    bind_value = create_json_node_list(full_key, rule, dd)
    try:
        check_func = _create_check(rule)
    except MatchConfigError, what:
        print(what)
        return []
    match_value = [bv for bv in bind_value if check_func(bv.data())]
    return match_value



