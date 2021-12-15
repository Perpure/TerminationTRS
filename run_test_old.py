import re
import sys
import itertools


def syntax_err(id=0, name=None):
    # print(id)
    # print(source)
    # if name != None:
    #     print(name)
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
    if str == '[]':
        return []
    regexp = r'^\[([a-zA-Z]+,)*[a-zA-Z]+]$'
    if not re.fullmatch(regexp, str):
        syntax_err(1)

    return str[1:-1].split(',')

def parse_terms(str):
    str = str.replace(' ', '')
    if re.search(r'\d', str) or not str.startswith(('first=', 'second=')):
        syntax_err(2)

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
    global is_duplicate_vars
    global variables
    regexp = r'^([a-zA-Z]+|([a-zA-Z]+\(.*\)))$'
    if not re.fullmatch(regexp, str):
        syntax_err(3)

    if not '(' in str:
        if str in used_vars:
            is_duplicate_vars = True
        else:
            used_vars.add(str)
        return (str)
    pos = str.index('(')
    func_name, remain = str[:pos], str[pos:]
    if func_name in variables:
        syntax_err(4)
    params = tuple([parse_term(term) for term in extract_params(remain[1:-1])])
    if func_name in arn_dict:
        if len(params) != arn_dict[func_name]:
            syntax_err(9)
    else:
        arn_dict[func_name] = len(params)
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
        syntax_err(5)
    global used_vars
    used_vars = set()
    term1 = parse_term(terms[0])
    used_vars = set()
    term2 = parse_term(terms[1])
    return (term1, term2)

def is_rule_useless(rule):
    if len(rule[0]) < 2:
        return False
    if isinstance(rule[0], tuple):
        if rule[1] in rule[0]:
            return True
    elif isinstance(rule[1], tuple):
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
                    if tmp == False:
                        return False
                    substitutions.update(tmp)
                return substitutions
            else:
                return False

        if is_const(term2):
            return False

        if term2 in tmp_variables:
            return {term2[0]: term1}

    if is_const(term1) and is_const(term2):
        if term1[0] != term2[0]:
            return False
        return dict()

    if term1 in tmp_variables:
        return {term1[0]: term2}

    return {term2[0]: term1}

def is_unificate(term1, term2):
    subst = get_substitutions(term1, term2)
    return True if subst else False

def apply_subst(term, subst):
    if term in subst:
        return subst[term]
    if isinstance(term, tuple):
        new_term = (term[0],)
        for i in range(1, len(term)):
            new_term += (apply_subst(term[i], subst),)
        return new_term
    return term

def unificate(term1, term2):
    subst = get_substitutions(term1, term2)
    return apply_subst(term1, subst) if subst else False

def flatten(term):
    if len(term) > 2:
        return False
    if len(term) == 2:
        tmp = flatten(term[1])
        if tmp == False:
            return False
        if tmp in variables:
            return term[0]
        return term[0] + tmp
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
arn_dict = dict()

def smart_replace(s, s_old, s_new):
    ans = []
    for start, end in [(m.start(), m.end()) for m in re.finditer(s_old, s)]:
        ans.append(s[:start] + s_new + s[end:])
    return ans

start_term = ''
def srs_dfs(term, depth=0):
    if depth != 0 and term == start_term:
        return True
    if depth == 6:
        global is_reached_limit
        is_reached_limit = True
        return False
    for rule in srs:
        if rule[0] in term:
            for new_term in smart_replace(term, rule[0], rule[1]):
                if srs_dfs(new_term, depth + 1):
                    return True


def is_greater(s1, s2, order):
    if len(s1) > len(s2):
        return True
    if len(s1) < len(s2):
        return False
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            if order.index(s1[i]) > order.index(s2[i]):
                return True
            return False
    return False

def is_greater2(s1, s2, order):
    for i in range(min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            if order.index(s1[i]) > order.index(s2[i]):
                return True
            return False
    if len(s1) > len(s2):
        return True
    return False

def check_lex_order():
    chars = list(set(''.join([rule[0] + rule[1] for rule in srs])))
    if len(chars) > 15:
        return
    for order in itertools.permutations(chars):
        is_good = True
        is_good2 = True
        for rule in srs:
            if not is_greater(rule[0], rule[1], order):
                is_good = False
            if not is_greater2(rule[0], rule[1], order):
                is_good2 = False
            if not is_good and not is_good2:
                break
        if is_good or is_good2:
            terminates()

def apply_rule(term, rule):
    ans = []
    if is_unificate(term, rule[0]):
        return [rule[1]]
    if isinstance(term, tuple):
        for i in range(1, len(term)):
            rest = apply_rule(term[i], rule)
            if rest != []:
                for new_term in rest:
                    ans.append(term[:i] + (new_term,) + term[i+1:])
    return ans

def rule_dfs(term, depth=0):
    if depth != 0 and is_unificate(start_term_trs, term):
        return True
    if depth > 5:
        return False
    for rule in rules:
        for new_term in apply_rule(term, rule):
            rule_dfs(new_term, depth + 1)

    return False

if __name__ == '__main__':
    with open('test.trs', 'r') as f:
        source = f.read()
        lines = list(filter(lambda x: x!= '', rm_junk.sub('', source).replace('\n\n', '\n').split('\n')))
        if len(lines) < 2:
            syntax_err(6)
        variables = parse_variables(lines[0])
        rules = []
        for line in lines[1:]:
            rule = parse_rule(line)
            rules.append(rule)


        if all([is_rule_useless(rule) for rule in rules]):
            terminates()
        if is_duplicate_vars:
            unknown()
        srs = SRS(rules)
        if srs:
            is_any_reached_limit = False
            for rule in srs:
                start_term = rule[0]

                is_reached_limit = False
                if srs_dfs(start_term):
                    print(source)
                    print(start_term)
                    print(srs)
                    not_terminates()
                is_any_reached_limit |= is_reached_limit
            # if not is_any_reached_limit:
            #     terminates()
            check_lex_order()
        else:
            for i in range(len(rules)):
                for j in range(i, len(rules)):
                    rule, rule1 = rules[i], rules[j]
                    start_term_trs = unificate(rule[0], rule1[0])
                    if start_term_trs and rule_dfs(start_term_trs):
                        not_terminates()
        unknown()


