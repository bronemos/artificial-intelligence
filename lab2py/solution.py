import sys
from test import *


def parse_input_resolution(clauses_path: str):
    with open(clauses_path, 'r', encoding='utf-8') as f:
        clauses = list(enumerate([x.strip()
                                  for x in f.readlines() if x[0] != '#'], start=1))


def parse_input_cooking(clauses_path: str, instructions_path: str):
    with open(clauses_path, 'r', encoding='utf-8') as f:
        clauses = list(enumerate([x.strip()
                                  for x in f.readlines() if x[0] != '#'], start=1))
    with open(instructions_path, 'r', encoding='utf-8') as f:
        instructions = list(
            enumerate([x.strip() for x in f.readlines() if x[0] != '#'], start=1))


def refutation_resolution():
    pass


def main():
    try:
        keyword = sys.argv[1]

        if keyword == 'resolution':
            parse_input_resolution(sys.argv[2])

        elif keyword == 'cooking':
            parse_input_cooking(*sys.argv[2:])

        else:
            print('Invalid keyword argument!', file=sys.stderr)
    except:
        print('Invalid number of arguments!', file=sys.stderr)


if __name__ == '__main__':
    main()
