import sys
from itertools import combinations, product
from collections import deque, defaultdict
from time import time


def get_resolution_list(given_clauses, goal_clause_negated, resolution_dict: defaultdict):
    resolution_list = list()
    resolution_list.append('NIL')
    to_check = deque()
    to_check.extend(resolution_dict['NIL'])
    while to_check:
        current = to_check.pop()
        to_check.extend(resolution_dict[current])
        resolution_list.append(current)
    resolution_list_ordered = list()
    separated = False
    for index, resolvent in enumerate(reversed(resolution_list), start=1):
        if resolvent != 'NIL':
            if resolvent not in given_clauses and resolvent != goal_clause_negated:
                if not separated:
                    splitter = index - 1
                    separated = True
                c1_index = resolution_list.index(resolution_dict[resolvent][1])
                c2_index = resolution_list.index(resolution_dict[resolvent][0])
                resolution_list_ordered.append((index,
                                                ' v '.join(
                                                    [literal if state else f"~{literal}" for literal, state in resolvent]), (c1_index, c2_index)))
            else:
                resolution_list_ordered.append((index,
                                                ' v '.join(
                                                    [literal if state else f"~{literal}" for literal, state in resolvent]), ''))
        else:
            c1_index = resolution_list.index(resolution_dict[resolvent][1])
            c2_index = resolution_list.index(resolution_dict[resolvent][0])
            resolution_list_ordered.append(
                (index, resolvent, (c1_index, c2_index)))
    return resolution_list_ordered, splitter


def print_resolution(resolution_dict: defaultdict, status, goal_clause, goal_clause_negated, given_clauses):
    if not status:
        print(
            f'[CONCLUSION]: {" v ".join([literal if state else f"~{literal}" for literal, state in goal_clause])} is unknown')
    else:
        resolution_list, splitter = get_resolution_list(
            given_clauses, goal_clause_negated, resolution_dict)
        print('\n'.join(
            [f'{index}. {clause} {origin}' for index, clause, origin in resolution_list[:splitter]]))
        print('='*15)
        print('\n'.join(
            [f'{index}. {clause} {origin}' for index, clause, origin in resolution_list[splitter:]]))
        print('='*15)
        print(
            f'[CONCLUSION]: {" v ".join([literal if state else f"~{literal}" for literal, state in goal_clause])} is true')


def parse_input_resolution(clauses_path: str):
    try:
        with open(clauses_path, 'r', encoding='utf-8') as f:
            lines = [x.strip().lower() for x in f.readlines() if x[0] != '#']
            all_clauses = [frozenset((literal, True) if literal[0] != '~' else (literal[1:], False)
                                     for literal in line.split(' v ')) for line in lines]
            clauses = set(all_clauses[:-1])
            goal_clause = all_clauses[-1]
            goal_clause_negated = frozenset((literal, not state)
                                            for literal, state in goal_clause)
            return clauses, goal_clause, goal_clause_negated
    except OSError as e:
        print('Invalid path!', file=sys.stderr)
        exit(1)


def parse_input_cooking(clauses_path: str, instructions_path: str):
    try:
        with open(clauses_path, 'r', encoding='utf-8') as f:
            clauses = list(
                enumerate([x.strip() for x in f.readlines() if x[0] != '#'], start=1))
        with open(instructions_path, 'r', encoding='utf-8') as f:
            instructions = list(
                enumerate([x.strip() for x in f.readlines() if x[0] != '#'], start=1))
    except OSError as e:
        print('Invalid path!', file=sys.stderr)
        exit(1)


def remove_redundant(resolvents):
    for c1, c2 in combinations(resolvents, 2):
        if c1.issubset(c2) and c2 in resolvents:
            resolvents.remove(c2)
        elif c2.issubset(c1) and c1 in resolvents:
            resolvents.remove(c1)
    return resolvents


def is_valid(resolvent):
    return not 2 * len(resolvent) == len(resolvent | set((literal, not state) for literal, state in resolvent))


def remove_irrelevant(resolvents):
    return set(resolvent for resolvent in resolvents if not is_valid(resolvent))


def resolve(c1, c2):
    c1 = set(c1)
    c2 = set(c2)
    for literal, state in set(c1):
        if (literal, not state) in c2:
            c1.remove((literal, state))
            c2.remove((literal, not state))
            if len(c1 | c2) == 0:
                return True
            else:
                return frozenset(c1 | c2)
    return False


def refutation_resolution(clauses, goal_clause_negated):
    resolution_dict = defaultdict(tuple)
    now = time()
    sos = set()
    sos.add(goal_clause_negated)
    clauses = remove_irrelevant(clauses)
    clauses = remove_redundant(clauses)
    while True:
        sos = remove_irrelevant(sos)
        sos = remove_redundant(sos)
        new = set()
        for c1, c2 in product(clauses | sos, sos):
            if c1 == c2:
                continue
            resolvent = resolve(c1, c2)
            if resolvent == False:
                continue
            elif resolvent == True:
                print(time() - now)
                resolution_dict['NIL'] = (c1, c2)
                return resolution_dict, True
            resolution_dict[resolvent] = (c1, c2)
            new.add(resolvent)
        if new.issubset(clauses | sos):
            return resolution_dict, False
        sos |= new


def main():
    try:
        keyword = sys.argv[1]
        if keyword == 'resolution':
            clauses, goal_clause, goal_clause_negated = parse_input_resolution(
                sys.argv[2])
            print_resolution(
                *refutation_resolution(clauses, goal_clause_negated), goal_clause, goal_clause_negated, clauses)

        elif keyword == 'cooking':
            parse_input_cooking(*sys.argv[2:])

        else:
            print('Invalid keyword argument!', file=sys.stderr)
            exit(1)
    except IndexError:
        print('Invalid number of arguments!', file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
