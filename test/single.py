
if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.realpath('.'))
import json


from jsonmatch.single import filter_with_single

new_data = json.loads(open('log/new.log').read())
rule = {'workers.[].apps.[].requests': {"min": 7000, "max": 0}}
match = filter_with_single(rule, new_data)
for i in match:
    print i