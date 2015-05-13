

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.realpath('.'))
import json

from jsonmatch.multiple import filter_with_multiple


old_data = json.loads(open('log/old.log').read())
new_data = json.loads(open('log/new.log').read())
filter = {
    'uid':{'max':300, 'key': 'E'},
    'workers.[].apps.[].modifier1': {'min':0,'max':1000, 'key': 'D'},
    'workers.*.running_time': {'min':0,'max':7000, 'key':'A'},
    'workers.*.requests': {'key':'B'}
}
# messages = filter_with_single(b, a)
list_convert_rule = {'workers.[]': ['id', 'pid'], 'workers.[].apps.[]': ['modifier1']}
formula = {'(A1 - A0)/(B1 - B0)': {'no': 500}}

# print json.dumps(list_convert_to_dict(list_convert_rule, a))
for i in filter_with_multiple(filter, formula, list_convert_rule, old_data, new_data):
    print i

