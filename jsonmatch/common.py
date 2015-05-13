# coding=utf-8

from jsonmatch.error import MatchKeyError, MatchConfigError
import os
import sys

work_path = os.path.realpath(__file__+"../../../")
if work_path not in sys.path:
    sys.path.append(work_path)


def getitem(ele, item):
    return ele[item]


def group_same_node(sources):
    d = {}
    for k, m in sources.iteritems():

        length = len(m)
        for mk in xrange(length):
            d[k] = type(m.value_list[0])()



class JsonNode(object):
    """
    how to get element:
    if you want to get same level other attr:
    m = Message(...)
    m[-1]['pid']
    if you don't know where is the 'pid' :
    m.get_attr('pid'),
    """
    def __init__(self, dd, full_key, rule, *args):
        assert isinstance(dd, dict)
        self.source = dd
        self.full_key_list = full_key
        self.rule = rule
        self.key_list = tuple(args)
        self.__init_value_list()

    def __init_value_list(self):
        search_list = self.key_list
        self.value_list = [self.source]
        search_list_len = len(search_list)
        for index in xrange(search_list_len):
            v = search_list[index]
            try:

                d = self.value_list[-1][v]
                self.value_list.append(d)
            except KeyError, what:
                raise MatchKeyError(
                    '%s has invalid key:<%s>%s' % (str(self), index, v)
                )
            except IndexError, what:
                raise MatchKeyError(
                    '%s has out of range index:<%s>%s' % (str(self), index, v)
                )
            except TypeError, what:
                raise MatchKeyError(
                    '%s has type error:<%s>%s%s' % (str(self), index, v, type(self.value_list[-1]))
                )
            except Exception, what:
                raise MatchKeyError(
                    '%s has unknow error:<%s>%s' % (str(self), index, v)
                )

    def deep_and_copy(self, *args):
        return self.__class__(self.source, self.full_key_list, self.rule, *(self.key_list + tuple(args)))

    def last(self):
        return self[-1]

    def data(self):
        return self[-1]

    def get_attr(self, key, top_level=0):
        assert isinstance(key, basestring)
        for i in xrange(len(self.key_list) - 1, top_level - 1, -1):
            if isinstance(self[i], (list, tuple)):
                continue
            elif isinstance(self[i], dict):
                ele = self[i].get(key)
                if ele is not None:
                    return ele
            else:
                continue
        return None

    def real_key(self):
        return '.'.join(str(i) for i in self.key_list)

    def __getitem__(self, item):
        return self.value_list[item]

    def __setitem__(self, item, value):
        self.value_list[item] = value
        for i in reversed(xrange(item)):
            self.value_list[i][self.key_list[i]] = self.value_list[i+1]

    def __len__(self):
        return len(self.key_list)

    def __str__(self):
        _data = self.data()
        if isinstance(_data, (tuple, list, dict)):
            _data = type(_data)
        return '{%s: %s}%s: %s' % ('.'.join(self.full_key_list), self.rule, self.real_key(), _data)

    __repr__ = __str__



def create_json_node_list(full_key, rule, dd):
    k_list = full_key.split('.')
    bind_value_list = [JsonNode(dd, k_list, rule)]

    def _analysis_list(_bv, __bind_value_list):
        if isinstance(_bv.data(), (list, tuple)):
            for __n in xrange(len(_bv.data())):
                sbv = _bv.deep_and_copy(__n)
                __bind_value_list.append(sbv)
            return True
        return False

    def _analysis_dict(_bv, __bind_value_list):
        if isinstance(_bv.data(), dict):
            for k in _bv.data().keys():
                sbv = _bv.deep_and_copy(k)
                __bind_value_list.append(sbv)
            return True
        return False

    for _k in k_list:
        _bind_value_list = []
        if _k == '*' or _k == '?':
            for bv in bind_value_list:
                try:
                    if not _analysis_list(bv, _bind_value_list) and not _analysis_dict(bv, _bind_value_list) and _k != '?':
                        #  TODO construct is so bad
                        raise MatchKeyError(
                            '%s has error key ==> <pos:%s>%s' % (str(bv), len(bv), _k))
                except MatchKeyError, what:
                    print(what)
        elif _k == '[]' or _k == '?[]':
            for bv in bind_value_list:
                try:
                    if not _analysis_list(bv, _bind_value_list) and _k != '?[]':
                        raise MatchKeyError(
                            '%s has error key ==> <pos:%s>%s' % (str(bv), len(bv), _k))
                except MatchKeyError, what:
                    print(what)
        elif _k == '{}' or _k == '?{}':
            for bv in bind_value_list:
                try:
                    if not _analysis_dict(bv, _bind_value_list) and _k != '?{}':
                        raise MatchKeyError(
                            '%s has error key ==> <pos:%s>%s' % (str(bv), len(bv), _k))
                except MatchKeyError, what:
                    print(what)

        else:
            for bv in bind_value_list:
                try:
                    if isinstance(bv.data(), (list, tuple)):
                        try:
                            _k = int(_k)
                        except ValueError, what:
                            #  TODO construct is so bad
                            raise MatchKeyError(
                                '%s has error key ==> <pos:%s>%s' % (str(bv), len(bv), _k))
                    _sbv = bv.deep_and_copy(_k)
                    _bind_value_list.append(_sbv)
                except MatchKeyError, what:
                    print(what)
        bind_value_list = _bind_value_list
    return bind_value_list


def _create_check(rule):
    if isinstance(rule, dict):
        def _dict_check(value):
            if 'not' in rule and value == rule['no']:
                return False
            if 'max' in rule and 'min' in rule:
                if rule['max'] < rule['min']:
                    return value < rule['max'] or value > rule['min']
                else:
                    return rule['min'] < value < rule['max']
            if 'max' in rule and value > rule['max']:
                return False
            elif 'min' in rule and value < rule['min']:
                return False
            return True
        return _dict_check
    else:
        def _simple_check(value):
            return rule == value
        return _simple_check