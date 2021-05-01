import sys
from itertools import combinations, product
from collections import deque, defaultdict
from time import time
from copy import deepcopy


def parse_input_resolution(clauses_path: str, goal_clause=None):
    try:
        with open(clauses_path, "r", encoding="utf-8") as f:
            lines = [x.strip().lower() for x in f.readlines() if x[0] != "#"]
            all_clauses = [
                frozenset(
                    (literal, True) if literal[0] != "~" else (literal[1:], False)
                    for literal in line.split(" v ")
                )
                for line in lines
            ]
            if goal_clause is None:
                clauses = set(all_clauses[:-1])
                goal_clauses = set(
                    frozenset(((literal, state),)) for literal, state in all_clauses[-1]
                )
            else:
                clauses = set(all_clauses)
                goal_clauses = set(
                    frozenset(((literal, True),))
                    if literal[0] != "~"
                    else frozenset(((literal[1:], False),))
                    for literal in goal_clause.split(" v ")
                )
            goal_clauses_negated = set()
            for clause in goal_clauses:
                goal_clauses_negated |= set(
                    frozenset(((literal, not state),)) for literal, state in clause
                )
            return clauses, goal_clauses, goal_clauses_negated
    except OSError:
        print("Invalid path!", file=sys.stderr)
        exit(1)


def parse_instructions_cooking(instructions_path: str):
    try:
        with open(instructions_path, "r", encoding="utf-8") as f:
            return [
                (x.strip().lower()[:-2], x.strip().lower()[-1])
                for x in f.readlines()
                if x[0] != "#"
            ]
    except OSError:
        print("Invalid path!", file=sys.stderr)
        exit(1)


def get_resolution_list(
    given_clauses, goal_clause_negated, resolution_dict: defaultdict
):
    resolution_list = list()
    given_used = list()
    resolution_list.append("NIL")
    to_check = deque()
    to_check.extend(resolution_dict["NIL"])
    while to_check:
        current = to_check.pop()
        if current in given_clauses or current in goal_clause_negated:
            given_used.append(current)
            continue
        to_check.extend(resolution_dict[current])
        resolution_list.append(current)
    resolution_list.extend(given_used)
    resolution_list_ordered = list()
    resolution_list.reverse()
    separated = False
    for index, resolvent in enumerate(resolution_list, start=1):
        if resolvent != "NIL":
            if resolvent not in given_clauses and resolvent not in goal_clause_negated:
                if not separated:
                    splitter = index - 1
                    separated = True
                c1_index = resolution_list.index(resolution_dict[resolvent][0]) + 1
                c2_index = resolution_list.index(resolution_dict[resolvent][1]) + 1
                resolution_list_ordered.append(
                    (
                        index,
                        " v ".join(
                            [
                                literal if state else f"~{literal}"
                                for literal, state in resolvent
                            ]
                        ),
                        (c1_index, c2_index),
                    )
                )
            else:
                resolution_list_ordered.append(
                    (
                        index,
                        " v ".join(
                            [
                                literal if state else f"~{literal}"
                                for literal, state in resolvent
                            ]
                        ),
                        "",
                    )
                )
        else:
            if not separated:
                splitter = index - 1
            c1_index = resolution_list.index(resolution_dict[resolvent][0]) + 1
            c2_index = resolution_list.index(resolution_dict[resolvent][1]) + 1
            resolution_list_ordered.append((index, resolvent, (c1_index, c2_index)))
    return resolution_list_ordered, splitter


def print_resolution(
    resolution_dict: defaultdict,
    status,
    goal_clause,
    goal_clause_negated,
    given_clauses,
):
    if not status:
        print(
            "\n".join(
                [
                    f"{index}. "
                    + " v ".join(
                        [
                            literal if state else f"~{literal}"
                            for literal, state in clause
                        ]
                    )
                    for index, clause in enumerate(given_clauses, start=1)
                ]
            )
        )
        print("=" * 15)
        print(
            f'[CONCLUSION]: {" v ".join([literal if state else f"~{literal}" for literal, state in [x for fs in goal_clause for x in fs]])} is unknown'
        )
    else:
        resolution_list, splitter = get_resolution_list(
            given_clauses, goal_clause_negated, resolution_dict
        )
        print(
            "\n".join(
                [
                    f"{index}. {clause} {origin}"
                    for index, clause, origin in resolution_list[:splitter]
                ]
            )
        )
        print("=" * 15)
        print(
            "\n".join(
                [
                    f"{index}. {clause} {origin}"
                    for index, clause, origin in resolution_list[splitter:]
                ]
            )
        )
        print("=" * 15)
        print(
            f'[CONCLUSION]: {" v ".join([literal if state else f"~{literal}" for literal, state in [x for fs in goal_clause for x in fs]])} is true'
        )


def remove_redundant(clauses, sos):
    for c1, c2 in combinations(clauses | sos, 2):
        if c1.issubset(c2):
            if c2 in sos:
                sos.remove(c2)
            elif c2 in clauses:
                clauses.remove(c2)
        elif c2.issubset(c1):
            if c1 in sos:
                sos.remove(c1)
            elif c1 in clauses:
                clauses.remove(c1)
    return clauses, sos


def is_valid(resolvent):
    return not 2 * len(resolvent) == len(
        resolvent | set((literal, not state) for literal, state in resolvent)
    )


def remove_irrelevant(clauses, sos):
    return set(resolvent for resolvent in clauses if not is_valid(resolvent)), set(
        resolvent for resolvent in sos if not is_valid(resolvent)
    )


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


def refutation_resolution(goal_clause, goal_clause_negated, clauses):
    resolution_dict = defaultdict(tuple)
    now = time()
    sos = set()
    sos |= goal_clause_negated
    given_clauses = deepcopy(clauses)
    while True:
        clauses, sos = remove_irrelevant(clauses, sos)
        clauses, sos = remove_redundant(clauses, sos)
        new = set()
        for c1, c2 in product(clauses | sos, sos):
            if c1 == c2:
                continue
            resolvent = resolve(c1, c2)
            if resolvent == False:
                continue
            elif resolvent == True:
                resolution_dict["NIL"] = (c1, c2)
                print_resolution(
                    resolution_dict,
                    True,
                    goal_clause,
                    goal_clause_negated,
                    given_clauses,
                )
                return
            resolution_dict[resolvent] = (c1, c2)
            new.add(resolvent)
        if new.issubset(clauses | sos):
            print_resolution(
                resolution_dict, False, goal_clause, goal_clause_negated, given_clauses
            )
            return
        sos |= new


def add_clause(clauses_path, clause):
    with open(clauses_path, "r") as f:
        lines = [x.strip().lower() for x in f.readlines()]
    lines.append(clause)
    with open(clauses_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"added {clause}")


def remove_clause(clauses_path, clause):
    with open(clauses_path, "r") as f:
        lines = [x.strip().lower() for x in f.readlines()]
    lines.remove(clause)
    with open(clauses_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"removed {clause}")


def print_clauses(clauses_path):
    print("Constructed with knowledge:")
    with open(clauses_path) as f:
        print("\n".join([x.strip() for x in f.readlines()]))


def main():
    keyword = sys.argv[1]
    if keyword == "resolution":
        clauses, goal_clause, goal_clause_negated = parse_input_resolution(sys.argv[2])
        refutation_resolution(goal_clause, goal_clause_negated, clauses)

    elif keyword == "cooking":
        print_clauses(sys.argv[2])
        instructions = parse_instructions_cooking(sys.argv[3])
        for literal, instruction in instructions:
            print(f"\nUser's command: {literal} {instruction}")
            clauses, goal_clause, goal_clause_negated = parse_input_resolution(
                sys.argv[2], goal_clause=literal
            )
            if instruction == "?":
                refutation_resolution(goal_clause, goal_clause_negated, clauses)
            elif instruction == "+":
                add_clause(sys.argv[2], literal)
            elif instruction == "-":
                remove_clause(sys.argv[2], literal)

    else:
        print("Invalid keyword argument!", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
