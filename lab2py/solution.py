import sys
from itertools import combinations


def parse_input_resolution(clauses_path: str):
    try:
        with open(clauses_path, 'r', encoding='utf-8') as f:
            lines = [frozenset(x.strip().lower().split(' v '))
                     for x in f.readlines() if x[0] != '#']
            clauses = set(enumerate(lines[:-1], start=1))
            goal_clause = lines[-1]
            return clauses, goal_clause
    except OSError as e:
        print('Invalid path!', file=sys.stderr)
        exit(1)


def parse_input_cooking(clauses_path: str, instructions_path: str):
    try:
        with open(clauses_path, 'r', encoding='utf-8') as f:
            clauses = list(enumerate([x.strip()
                                      for x in f.readlines() if x[0] != '#'], start=1))
        with open(instructions_path, 'r', encoding='utf-8') as f:
            instructions = list(
                enumerate([x.strip() for x in f.readlines() if x[0] != '#'], start=1))
    except:
        print('Invalid path!', file=sys.stderr)
        exit(1)


def remove_redundant(clauses: set):
    redundant = set()

    for c1, c2 in combinations(clauses, 2):
        if len(c1 - c2) == 0:
            redundant.add(c2)
        elif len(c2 - c1) == 0:
            redundant.add(c1)

    return clauses - redundant


def is_irrelevant(clause: str):
    removed_negation = clause.replace('~', '').split(' v ')
    return len(removed_negation) != len(set(removed_negation))


def remove_irrelevant(clauses: set):
    irrelevant = set()
    for clause in clauses:
        if is_irrelevant(clause):
            irrelevant.add(clause)

    return clauses - irrelevant


def refutation_resolution(clauses: set, goal_clause: str):
    new = set()
    for c1, c2 in combinations(clauses, 2):
        print(c1, c2)


def main():
    try:
        keyword = sys.argv[1]
        if keyword == 'resolution':
            clauses, goal_clause = parse_input_resolution(sys.argv[2])
            refutation_resolution(clauses, goal_clause)

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
