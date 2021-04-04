import argparse
import time
from collections import deque
from queue import PriorityQueue

start = time.time()


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
        goal_states = set(path_data[1].split(' '))
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


def bfs(initial_state: str, goal_states: set, state_dict: dict, *_):
    open_queue = deque([initial_state])
    parent_dict = dict()
    visited = set()

    while open_queue:
        current_state = open_queue.popleft()
        visited.add(current_state)
        children = state_dict[current_state]

        for child_name, child_cost in children:
            if child_name not in visited:
                parent_dict[child_name] = (current_state, child_cost)
                visited.add(child_name)
                open_queue.append(child_name)

            if child_name in goal_states:
                path, cost = backtrace(
                    initial_state, child_name, parent_dict)
                print(time.time() - start)
                print_output('BFS', 'yes', len(visited), len(path), cost, path)


def ucs(initial_state: str, goal_states: set, state_dict: dict, *_):
    open_list = PriorityQueue()
    open_list.put((0, initial_state))
    parent_dict = dict()
    total_cost_dict = dict()
    visited = set()

    while open_list:
        current_state_cost, current_state_name = open_list.get()
        visited.add(current_state_name)
        if current_state_name in goal_states:
            path, cost = backtrace(
                initial_state, current_state_name, parent_dict)
            print(time.time() - start)
            print_output('UCS', 'yes', len(visited), len(path), cost, path)

        children = state_dict[current_state_name]

        for child_name, child_cost in children:
            if (child_name not in parent_dict or total_cost_dict[child_name] > current_state_cost + child_cost) and child_name not in visited:
                parent_dict[child_name] = (current_state_name, child_cost)
                total_cost_dict[child_name] = child_cost + current_state_cost
                open_list.put((child_cost + current_state_cost, child_name))


def generate_heuristic_dict(heuristic_path: str):
    with open(heuristic_path, encoding='utf-8') as f:
        return {k: float(v) for k, v in [x.split(': ') for x in f.readlines() if x[0] != '#']}


def astar(initial_state: str, goal_states: set, state_dict: dict, heuristic_path: str, check_consistent, check_optimistic):
    heuristic_dict = generate_heuristic_dict(heuristic_path)
    open_list = PriorityQueue()
    open_list.put((0 + heuristic_dict[initial_state], initial_state))
    visited = set()

    while open_list:
        current_state = open_list.get()
        visited.add(current_state[1])
        if current_state[1] in goal_states:
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
