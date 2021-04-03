import argparse
import time


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--alg', required=True, metavar='algorithm',
                        choices=['bfs', 'ucs', 'astar'])
    parser.add_argument('--ss', metavar='state_descriptor', required=True)
    parser.add_argument('--h', metavar='heuristic_descriptor')
    parser.add_argument('--check-optimistic', action='store_true')
    parser.add_argument('--check-consistent', action='store_true')

    return parser


def print_output(alg, found_solution, states_visited, path_length, path_cost, path):
    print(f'# {alg}\n'
          f'[FOUND_SOLUTION]: {found_solution}\n'
          f'[STATES_VISITED]: {states_visited}\n'
          f'[PATH_LENGTH]: {path_length}\n'
          f'[TOTAL_COST]: {path_cost}\n'
          f'[PATH]: {" => ".join(path)}')
    exit(0)


def generate_state_dict(path: str):
    with open(path, encoding='utf-8') as f:
        path_data = [x.strip() for x in f.readlines() if x[0] != '#']
        initial_state = path_data[0]
        goal_states = path_data[1].split(' ')
        state_dict = {k: sorted(tuple((y.split(',')[0], float(y.split(',')[1])) for y in v.split(' ')), key=lambda x: x[0]) if len(v) > 0 else tuple()
                      for k, v in [x.split(': ') if len(x.split(': ')) > 1 else [x[:-1], []] for x in path_data[2:]]}
        return initial_state, goal_states, state_dict


def backtrace(initial_state, goal_state, parent_dict):
    cost = 0
    path = [goal_state]
    current_state = goal_state
    while current_state != initial_state:
        cost += parent_dict[current_state][1]
        current_state = parent_dict[current_state][0]
        path.append(current_state)
    return list(reversed(path)), cost


def bfs(initial_state: str, goal_states: str, state_dict: dict, *_):
    start = time.time()
    open_list = [initial_state]
    parent_dict = dict()
    visited = set()
    while len(open_list) > 0:
        current_state = open_list.pop(0)
        visited.add(current_state)
        children = state_dict[current_state]

        for child in children:
            if child[0] not in visited:
                parent_dict[child[0]] = (current_state, child[1])
                visited.add(child[0])
                open_list.append(child[0])

            if child[0] in goal_states:
                path, cost = backtrace(
                    initial_state, child[0], parent_dict)
                print(time.time() - start)
                print_output('BFS', 'yes', len(visited), len(path), cost, path)


def ucs(initial_state: str, goal_states: str, state_dict: dict, *_):
    pass


def astar(initial_state: str, goal_states: str, state_dict: dict, heuristic, check_consistent, check_optimistic):
    pass


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if args.alg == 'astar' and not args.h:
        parser.error('--alg astar requires --h heuristic_descriptor')

    initial_state, goal_states, state_dict = generate_state_dict(args.ss)
    alg_dict = {'bfs': bfs,
                'ucs': ucs,
                'astar': astar}
    alg_dict[args.alg](initial_state, goal_states, state_dict,
                       args.h, args.check_consistent, args.check_consistent)
