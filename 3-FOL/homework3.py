import copy
import itertools
import time


class Literal:
    # Suppose all literals are Predicate(Arguments: Constant | Variable)
    def __init__(self):
        self.negate = False
        self.predicate = ''
        self.arguments = []
        self.constants = []
        self.variables = []

    def print(self):
        print('--------------------------')
        print('Negate:', self.negate)
        print('Predicate:', self.predicate)
        print('Arguments:', self.arguments)
        print('Constant:', self.constants)
        print('Variables:', self.variables)
        print('--------------------------')

    def string(self):
        sentence = '~' if self.negate else ''
        sentence = sentence + self.predicate + '('
        for j in range(len(self.arguments)):
            sentence = sentence + self.arguments[j]
            sentence += ')' if j == (len(self.arguments) - 1) else ','
        return sentence

    def pair(self):
        pair = (self.negate, self.predicate, self.arguments)
        return pair

    def __eq__(self, other):
        return self.negate == other.negate and self.predicate == other.predicate and self.arguments == other.arguments


def parse(sentence):
    literal = Literal()
    sentence = sentence.replace(' ', '')
    predicate = sentence[:sentence.find('(')]
    arguments = sentence[sentence.find('(') + 1:sentence.find(')')].split(',')
    if predicate[0] == '~':
        literal.negate = True
        predicate = predicate.replace('~', '')

    literal.predicate = predicate
    for arg in arguments:
        if arg[0].isupper():
            literal.constants.append(arg)
        else:
            literal.variables.append(arg)
        literal.arguments.append(arg)
    # term.print()
    return literal


def implication_elimination(rule):
    # Only think about A & B => C first
    implication = rule.find('=')
    front = rule[:implication]
    literals = front.split('&')
    if implication != -1:
        if len(literals) > 1:
            rule = '~(' + rule[:implication] + ')|' + rule[implication + 2:]
        else:
            rule = '~' + rule[:implication] + '|' + rule[implication + 2:]
    else:
        rule = rule
    return rule


def move_negate_inward(rule):
    if rule.find('|') != -1:
        separate = rule.split('|')
        premise = separate[0][1:] if separate[0][1] != '(' else separate[0][2:-1]
        conclusion = separate[1]
        premise_literals = premise.split('&')
        for j in range(len(premise_literals)):
            if premise_literals[j][0] != '~':
                premise_literals[j] = '~' + premise_literals[j]
            else:
                premise_literals[j] = premise_literals[j][1:]
        rule = '|'.join(premise_literals) + '|' + conclusion
    return rule


def convert_cnf(rule):
    # No other operators besides &, =>, and ~ are used in the knowledge base
    # There will be no parentheses in the KB except as used to denote arguments of predicates
    # A given predicate name will not appear with different number of arguments
    rule = rule.replace(' ', '')
    rule = implication_elimination(rule)
    rule = move_negate_inward(rule)
    return rule


def substitute(literal, substitution):
    if substitution:
        for index, argument in enumerate(literal.arguments):
            if argument in substitution:
                # print(arg, 'in Set')
                literal.arguments[index] = substitution[argument]
                # print('Replace', arg, 'with', substitution[arg])
                if substitution[argument][0].islower():
                    # print(substitution[arg], 'is Variable')
                    literal.variables.remove(argument)
                    # print('Remove', literal.arguments[index], 'from literal.variables')
                    literal.variables.append(substitution[argument])
                    # print('Add', substitution[arg], 'to literal.variables')
                else:
                    literal.variables.remove(argument)
                    # print('Remove', literal.arguments[index], 'from literal.variables')
                    literal.constants.append(substitution[argument])
                    # print('Add', substitution[arg], 'to literal.constants')
    return literal


def unify_variable(argument1, argument2, unify_set):
    if argument1 in unify_set:
        # print('Argument1 in Set:', argument1)
        return unify_literal(unify_set[argument1], argument2, unify_set)
    elif argument2 in unify_set:
        # print('Argument2 in Set:', argument2)
        return unify_literal(argument1, unify_set[argument2], unify_set)
    else:
        # print('Argument not in Set:', argument1, 'replace by', argument2)
        unify_set[argument1] = argument2
        return unify_set


def unify_literal(arguments1, arguments2, unify_set=None):
    # Same predicate has same length of arguments
    if unify_set is None:
        unify_set = {}
    if unify_set is False:
        return False
    elif arguments1 == arguments2:
        return unify_set
    elif type(arguments1) == list and type(arguments2) == list:
        if arguments1 and arguments2:
            new_unify_set = unify_literal(arguments1[0], arguments2[0], unify_set)
            return unify_literal(arguments1[1:], arguments2[1:], new_unify_set)
        else:
            return unify_set
    else:
        if unify_set is False:
            return False
        if arguments1[0].islower():
            # print('First argument is variable:', arguments1, unify_set)
            return unify_variable(arguments1, arguments2, unify_set)
        elif arguments2[0].islower():
            # print('Second argument is variable', arg2, unify_set)
            return unify_variable(arguments2, arguments1, unify_set)
        elif arguments1 != arguments2:
            return False


def resolve(sentence1, sentence2):
    copy1, copy2 = copy.deepcopy(sentence1), copy.deepcopy(sentence2)
    new_rules = []
    for l1 in copy1:
        for l2 in copy2:
            unification = False
            if l1.negate != l2.negate and l1.predicate == l2.predicate:
                if len(l1.constants) or len(l2.constants):
                    # Unify when constant(s) exists
                    unification = unify_literal(l1.arguments, l2.arguments)
            if unification is not False:
                rest1 = copy.deepcopy(copy1)
                rest2 = copy.deepcopy(copy2)
                rest1 = [x for x in rest1 if
                                   x.arguments != l1.arguments or x.predicate != l1.predicate]
                rest2 = [x for x in rest2 if
                                   x.arguments != l2.arguments or x.predicate != l2.predicate]
                if not rest1 and not rest2:
                    # If no more left in both sentences = Contradiction found
                    return False
                rest1 = [substitute(x, unification) for x in rest1]
                rest2 = [substitute(x, unification) for x in rest2]
                new_rule = union(rest1, rest2)
                new_rules.append(new_rule)
    return new_rules


def union(list1, list2):
    """
    Get the union of list1 and list2
    which are new rules and KB
    """
    new_list = list1
    for literal in list2:
        negate_literal = copy.deepcopy(literal)
        negate_literal.negate = not negate_literal.negate
        if negate_literal in list1:
            new_list.remove(negate_literal)
            continue
        if literal not in list1:
            new_list.append(literal)
    return new_list


def allin(list1, list2):
    """
    Check if list1 is all in list2
    """
    for rule1 in list1:
        literals1 = [literal for literal in rule1]
        for rule2 in list2:
            literals2 = [literal for literal in rule2]
            if literals1 != literals2:
                # If there is one rule different, then is not a sublist
                return False
    return True


def difference(list1, list2):
    """
    Get the difference of list1 (new rules) and list2 (KB)
    Remove the same rules
    """
    new_list = []
    for rule1 in list1:
        in_list2 = False
        literals1 = [x.string() for x in rule1]
        for rule2 in list2:
            literals2 = [x.string() for x in rule2]
            if literals1 == literals2:
                in_list2 = True
        if not in_list2:
            new_list.append(rule1)
    return new_list


def filter_kb(kb, q):
    """
    Get the rules related to query by removing unusable rules
    """
    new_kb = []
    related_predicate = set()
    related_predicate.add(q.predicate)
    history = []
    j = 0
    while j < len(kb):
        all_literals = [literal for literal in kb[j]]
        check = any(literal.predicate in related_predicate for literal in all_literals)
        if check:
            for literal in all_literals:
                if literal.predicate not in related_predicate:
                    related_predicate.add(literal.predicate)
            if kb[j] not in history:
                new_kb.append(kb[j])
                history.append(kb[j])
                j = -1
        j += 1
    return new_kb


def unit_resolution(kb):
    """
    Unit Resolute rules if there are single-literal rules and with only variables
    E.g. A(x) | B(x) => A(x) = B(x)
    """
    history = None
    new_kb = copy.deepcopy(kb)
    while True:
        single_literal = []
        multiple_literal = []
        for rule in new_kb:
            literals = rule
            if len(literals) == 1 and len(literals[0].constants) == 0:
                single_literal.append(rule)
            else:
                multiple_literal.append(rule)
        if not single_literal or not multiple_literal:
            return new_kb
        elif [x[0].string() for x in single_literal] == history:
            return new_kb
        single_left = []
        for literal1 in single_literal:
            resolved = False
            for literals2 in multiple_literal:
                j = 0
                while j < len(literals2):
                    if '~' + literal1[0].string() == literals2[j].string():
                        literals2.remove(literals2[j])
                        j -= 1
                        resolved = True
                    elif literal1[0].string()[1:] == literals2[j].string():
                        literals2.remove(literals2[j])
                        j -= 1
                        resolved = True
                    elif literal1[0].predicate == literals2[j].predicate and literal1[0].negate != literals2[j].negate:
                        if len(literals2[j].constants) == 0:
                            literals2.remove(literals2[j])
                            j -= 1
                            resolved = True
                    j += 1
            if not resolved:
                single_left.append(literal1)
        new_kb = copy.deepcopy(multiple_literal)
        new_kb += single_left
        history = [x[0].string() for x in single_literal]


def factor_statements(kb):
    """
    Factoring rules to remove same predicates =
    Unify literals within the same rule
    """
    # Unify literals in same rule
    for rule in kb:
        for index, literal1 in enumerate(rule):
            rest = rule[index + 1:]
            for literal2 in rest:
                if literal1.negate == literal2.negate and literal1.predicate == literal2.predicate:
                    unification = unify_literal(literal1.arguments, literal2.arguments)
                    if unification is False:
                        continue
                    else:
                        for literal in rule:
                            substitute(literal, unification)
    # Remove same literals
    new_kb = []
    for rule in kb:
        new_rule = []
        for literal in rule:
            if literal not in new_rule:
                new_rule.append(literal)
        new_kb.append(new_rule)
    return new_kb


def resolution(kb, q):
    """
    Main resolution
    """
    # start = time.time()
    # Remove rules not related to proving query
    kb = filter_kb(kb, q)
    # Unit resolute to remove single-literal with variables only
    kb = unit_resolution(kb)
    # Factor rules to remove same literals in same rule
    kb = factor_statements(kb)
    # Sort rule to prevent same rule in different order
    for rule in kb:
        rule.sort(key=lambda x: x.predicate)
    # Insert negated query to kb
    kb.insert(0, [q])
    # Keep track of resolved two rules
    history = {}
    loop = 0
    while True:
        # Store new rules
        new_rules = []
        # Store string version of new rules
        for pair in itertools.combinations(kb, 2):
            rule1, rule2 = pair[0], pair[1]
            literals1 = str([x.string() for x in rule1])
            literals2 = str([x.string() for x in rule2])
            has_checked = False
            if literals1 in history:
                # If already have rule1 in history
                has_checked = True
                if literals2 in history[literals1]:
                    # If already have rule1 in history paired with rule2
                    continue
            if has_checked:
                history[literals1].add(literals2)
            else:
                history[literals1] = set()
                history[literals1].add(literals2)
            # print(str([x.string() for x in rule1]), str([x.string() for x in rule2]))
            resolvent = resolve(rule1, rule2)
            if loop > 30000:
                # A kill threshold
                # If takes too long, usually infinitely extending KB
                # print(time.time() - start, len(kb))
                return False
            if resolvent is False:
                # If contradiction found then True
                # Removed has to relates to query since KB won't have contradiction
                return True
            for rule in resolvent:
                # Sort rule to prevent same rule in different order
                rule.sort(key=lambda x: x.predicate)
                if rule not in new_rules:
                    new_rules.append(rule)
            loop += 1
        if allin(new_rules, kb):
            # If new rules are all in KB already = no more new knowledge
            return False
        # Get the rules not in KB yet
        new_rules = difference(new_rules, kb)
        # Factoring rules for new rules
        new_rules = factor_statements(new_rules)
        for rule in new_rules:
            kb.append(rule)


file = open('input.txt', 'r')
query_amount = int(file.readline().strip())
queries = []
for i in range(query_amount):
    line = file.readline().strip()
    query = parse(line)
    query.negate = not query.negate
    queries.append(query)

KB_amount = int(file.readline().strip())
KBs = []
for i in range(KB_amount):
    KB = []
    line = file.readline().strip()
    line = convert_cnf(line)
    if line.find('|') > -1:
        temp = line.split('|')
        for t in temp:
            KB.append(parse(t))
    else:
        KB.append(parse(line))
    KBs.append(KB)

file.close()

results = []
for query in queries:
    answer = str(resolution(copy.deepcopy(KBs), query)).upper()
    results.append(answer)
    print(answer)

output = open('output.txt', 'w')
for result in results:
    print(result, file=output)
output.close()
