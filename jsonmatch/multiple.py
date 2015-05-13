# coding=utf-8
import re
from copy import deepcopy

from jsonmatch.common import create_json_node_list, getitem, _create_check


class MultipleMessage(object):
    def __init__(self, formula, **kwargs):
        """
        :param formula: (formula_str, filter_val)
        :param kwargs: {}
        """
        self.source = kwargs
        self.vars = {k: m.data() for k, m in kwargs.iteritems()}
        self.formula = formula
        self.check = _create_check(formula[1])
        # print 'formula:', formula[0], 'var:', self.vars
        try:
            self.value = eval(self.formula[0], self.vars)
        except ZeroDivisionError, what:
            self.value = what

    def data(self):
        return self.value

    def __str__(self):
        _list = ['%s: %s\n' % (k, str(m)) for k, m in self.source.iteritems()]
        return ''.join(_list) + '%s: %s' % (self.formula[0],self.value)

    __repr__ = __str__

    def report(self):
        limit = self.formula[1]
        name = limit['name'] if 'name' in limit else self.formula[0]

        if isinstance(limit, dict):
            format_str = '(%s)%s: %s' + '(range:%s - %s)' % (limit.get('min', '-∞'), limit.get('max', '∞'))
        else:
            format_str = '(%s)%s: %s' + '(limit:%s)' % limit
        msg = format_str % (
            ', '.join('%s: {%s: %s}' % (f, msg.real_key(), msg.data()) for f, msg in self.source.iteritems()),
            name,
            self.value
        )
        return msg

    def is_normal(self):
        return self.check(self.data())


class MessageTree(dict):
    def to_list(self):
        _list = []
        for k, v in self.iteritems():
            if isinstance(v, MessageTree):
                _v = v.to_list()
            else:
                _v = v
            _list.append((k, _v))
        _list.sort(key=lambda x: x[0])
        return _list


def filter_with_multiple(filter_rule, formula, list_group_rule, *args):
    level_messages = []
    dd_array = (list_convert_to_dict(list_group_rule, dd) for dd in args)

    __filter_rule = {k.replace('.[].', '.*.'): v for k, v in filter_rule.iteritems()}
    for __dd in dd_array:
        message_list = []
        for key, rule in __filter_rule.iteritems():
            if isinstance(rule, dict) and 'key' in rule:
                message_list.extend(create_json_node_list(key, rule, __dd))
        level_messages.append(sorted(message_list, key=lambda x: x.key_list, reverse=True))
    # filter with 'key'
    level_trees = messages_to_tree(*level_messages)
    mmsg_list = create_mutli_message(level_trees, formula)

    return [mmsg for mmsg in mmsg_list if mmsg.is_normal()]


def list_convert_to_dict(list_match_rule, dd):
    for list_dir, signs in list_match_rule.iteritems():
        new_dd = deepcopy(dd)
        list_dir.replace('.[].', '.*.')
        dirs = find_list(dd, list_dir, signs)
        items_list = [s.split('.') for s in signs]
        for _dir in dirs:
            key = (reduce(getitem, [_dir.data()] + items) for items in items_list)
            key = '-'.join(str(i) for i in key)
            if not _dir.key_list[:-2]:
                widget_array = new_dd
            else:
                widget_array = reduce(getitem, (new_dd,) + _dir.key_list[:-2])
            if isinstance(widget_array[_dir.key_list[-2]], list):
                widget_array[_dir.key_list[-2]] = {}
            widget_array[_dir.key_list[-2]].update({key: _dir.data()})
            # print '_dir change---------', _dir[-2]
        # print 'new_dd:\n', new_dd
        # print 'dd:\n', dd
        dd = new_dd
    return dd


def get_var_names(dd_var_rule):
    """
    :param dd_var_rule: just like {"(A0 * B0 - A1 * B1)/(B1 - B0)": {"max:" 20}, ...}
    :return: {"(A0 * B0 - A1 * B1)/(B1 - B0)": [('A0','B0','A1','B1')], ...}
    """
    rst = {}
    for k in dd_var_rule.keys():
        # print 'k:',k
        var_list = re.split(r'[\+\-\*/\(\) ]|int|float', k)
        var_set = set(var_list)

        var_set.discard('')
        del_set = set()
        for v in var_set:
            if v.isdigit():
                del_set.add(v)
        del_set.add('')
        var_set -= del_set
        rst[k] = var_set
    # print 'get_var_names', rst

    return rst


def run_tree(tree, **_global):
    """
    :param tree: MessageTree
    :param _global: global args
    :return: [global args, local args]
    """
    after = {}
    _local = {}
    # print 'tree',tree
    for k, v in tree.iteritems():
        if isinstance(v, MessageTree):
            after[k] = v
        else:
            # print '_local_value:', k, v
            _local[k] = v

    for k, v in after.iteritems():
        for widget in run_tree(v, **dict(_global, **_local)):
            yield widget
    yield (_global, _local)


def create_mutli_message(tree, rule):
    mmsg_list = []
    var_attr_dict = get_var_names(rule)
    for glo, _local in run_tree(tree):
        all_var = dict(glo, **_local)

        all_names = set(all_var.keys())
        local_names = set(_local.keys())
        for rk, var_names in var_attr_dict.iteritems():
            # make sure the var_names ⊆ all_names and some var in local_names(local_names was change at next loop)
            if all_names >= var_names and local_names & var_names:
                mmsg = MultipleMessage((rk, rule[rk]), **{v: all_var[v] for v in var_names})
                mmsg_list.append(mmsg)
    return mmsg_list


def messages_to_tree(*args):
    """
    :param args: [message_list1, message_list2, message_list3]
    :param message_list: [msg1, msg2, msg3]
    :return: tree mode:
                {k0:num, k1:num, v0:num, v1:num, ..., key:{...}, key:{...}}
                                                     /                   \
                     {k0:num, k1:num, ..., key:{...}}                  {k0:num, k1:num, ..., key:{...}}

    """
    tree = MessageTree()
    for i in xrange(len(args)):
        message_list = args[i]
        for msg in message_list:
            if len(msg.key_list) >= 1:
                pos = create_pos_with_tree(tree, msg.key_list[:-1])
                pos[msg.rule['key']+str(i)] = msg
    return tree


def create_pos_with_tree(_dict_data, key_list):
    _pos = _dict_data
    for k in key_list:
        if k not in _pos:
            _pos[k] = MessageTree()
        _pos = _pos[k]
    return _pos


def find_list(data, list_dir, sign):
    return create_json_node_list(list_dir, sign, data)

