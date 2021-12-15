import re
import sys


def syntax_err():
    with open('result', 'w') as f:
        f.write('Syntax error')
    exit(0)

def terminates():
    with open('result', 'w') as f:
        f.write('True')
    exit(0)

def unknown():
    with open('result', 'w') as f:
        f.write('Unknown')
    exit(0)

def not_terminates():
    with open('result', 'w') as f:
        f.write('False')
    exit(0)

def parse_variables(str):
    regexp = r'^\[([a-zA-Z],)*[a-zA-Z]]$'
    if not re.fullmatch(regexp, str):
        syntax_err()

    return str[1:-1].split(',')

def parse_terms(str):
    str = str.replace(' ', '')
    if re.search(r'\d', str) or not str.startswith(('first=', 'second=')):
        syntax_err()

    return parse_term(str.split('=')[1])

def extract_params(str):
    # split parameters by commas out of brackets
    res = ['']
    balance = 0
    for c in str:
        if balance > 0:
            raise ValueError('Wrong terms syntax')
        if c == ',' and balance == 0:
            res.append('')
        else:
            res[-1] += c
            if c == '(':
                balance -= 1
            elif c == ')':
                balance += 1
    return res

is_duplicate_vars = False
used_vars = set()
def parse_term(str):
    regexp = r'^([a-zA-Z]+|([a-zA-Z]+\(.*\)))$'
    if not re.fullmatch(regexp, str):
        syntax_err()

    if not '(' in str:
        if str in variables:
            syntax_err()
        else:
            if str in used_vars:
                is_duplicate_vars = True
            else:
                used_vars.add(str)
            return (str)
    pos = str.index('(')
    func_name, remain = str[:pos], str[pos:]
    params = tuple([parse_term(term) for term in extract_params(remain[1:-1])])
    return (func_name,) + params

def is_const(term):
    return not term[0] in variables

def is_variable(term):
    return term[0] in variables

def is_func(term):
    return len(term) != 1

def parse_rule(s):
    terms = s.split('->')
    if len(terms) != 2:
        syntax_err()
    global used_vars
    used_vars = set()
    term1 = parse_term(terms[0])
    used_vars = set()
    term2 = parse_term(terms[1])
    return (term1, term2)

def is_rule_useless(rule):
    if len(rule[0]) < 2:
        return False
    if rule[1] in rule[0]:
        return True
    for term in rule[0][1:]:
        if is_rule_useless((term, rule[1])):
            return True
    return False


def rename_vars(term, postfix):
    for i in range(len(term)):
        if is_variable(term[i]):
            term[i] += postfix
        elif isinstance(term[i], list):
            term[i] = rename_vars(term, postfix)


def get_substitutions(term1, term2):
    substitutions = dict()
    tmp_variables = []
    for var in variables:
        tmp_variables += [var + '1', var + '2']

    if is_func(term2):
        term1, term2 = term2, term1

    if is_func(term1):
        if is_func(term2):
            if term1[0] == term2[0] and len(term1) == len(term2):
                for i in range(1, len(term1)):
                    tmp = get_substitutions(term1[i], term2[i])
                    if tmp == None:
                        return None
                    substitutions.update(tmp)
                return substitutions
            else:
                return None

        if is_const(term2):
            return None

        if term2 in tmp_variables:
            return {term2[0]: term1}

    if is_const(term1) and is_const(term2):
        if term1[0] != term2[0]:
            return None
        return dict()

    if term1 in tmp_variables:
        return {term1[0]: term2}

    return {term2[0]: term1}

def flatten(term):
    if len(term) > 2:
        return False
    if len(term) == 2:
        return term[0] + flatten(term[1])
    return term[0]

def SRS(rules):
    new_rules = []
    for rule in rules:
        new_rule1 = flatten(rule[0])
        new_rule2 = flatten(rule[1])
        if not new_rule1 or not new_rule2:
            return False
        new_rules.append((new_rule1, new_rule2))
    return new_rules

rm_junk = re.compile(r'[ \r\t]')
if __name__ == '__main__':
    with open('test.trs', 'r') as f:
        lines = rm_junk.sub('', f.read()).replace('\n\n', '\n').split('\n')
        if len(lines) < 2:
            syntax_err()
        variables = parse_variables(lines[0])
        rules = []
        for line in lines[1:]:
            rule = parse_rule(line)
            rules.append(rule)
        if len(rules) == 0:
            terminates()


