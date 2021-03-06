import argparse
import time
from collections import deque
import heapq

start = time.time()
measure_time = False

alg_name_dict = {"bfs": "BFS", "ucs": "UCS", "astar": "A-STAR"}


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--alg", metavar="algorithm", choices=["bfs", "ucs", "astar"])
    parser.add_argument("--ss", metavar="state_descriptor", required=True)
    parser.add_argument("--h", metavar="heuristic_descriptor")
    parser.add_argument("--check-optimistic", action="store_true")
    parser.add_argument("--check-consistent", action="store_true")
    parser.add_argument("--t", action="store_true")

    return parser


def print_output(
    alg, found_solution, states_visited, path_length, path_cost, path, heuristic=None
):
    title = (
        alg_name_dict[alg]
        if not heuristic
        else " ".join([alg_name_dict[alg], heuristic])
    )
    print(
        f"# {title}\n"
        f"[FOUND_SOLUTION]: {found_solution}\n"
        f"[STATES_VISITED]: {states_visited}\n"
        f"[PATH_LENGTH]: {path_length}\n"
        f"[TOTAL_COST]: {path_cost}\n"
        f'[PATH]: {" => ".join(path)}'
    )


def generate_state_dict(
    path: str, sort_children: bool = False, sort_nodes: bool = False
):
    with open(path, encoding="utf-8") as f:
        path_data = [x.strip() for x in f.readlines() if x[0] != "#"]
        initial_state = path_data[0]
        goal_states = set(path_data[1].split(" "))
        if sort_children:
            state_dict = {
                k: sorted(
                    tuple(
                        (y.split(",")[0], float(y.split(",")[1])) for y in v.split(" ")
                    ),
                    key=lambda x: x[0],
                )
                if len(v) > 0
                else tuple()
                for k, v in [
                    x.split(": ") if len(x.split(": ")) > 1 else [x[:-1], []]
                    for x in path_data[2:]
                ]
            }
        elif sort_nodes:
            state_dict = {
                k: tuple(
                    (y.split(",")[0], float(y.split(",")[1])) for y in v.split(" ")
                )
                if len(v) > 0
                else tuple()
                for k, v in [
                    x.split(": ") if len(x.split(": ")) > 1 else [x[:-1], []]
                    for x in sorted(path_data[2:])
                ]
            }
        else:
            state_dict = {
                k: tuple(
                    (y.split(",")[0], float(y.split(",")[1])) for y in v.split(" ")
                )
                if len(v) > 0
                else tuple()
                for k, v in [
                    x.split(": ") if len(x.split(": ")) > 1 else [x[:-1], []]
                    for x in path_data[2:]
                ]
            }
        return initial_state, goal_states, state_dict


def backtrace(initial_state, goal_state, parent_dict):
    cost = 0.0
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
                path, cost = backtrace(initial_state, child_name, parent_dict)
                if measure_time:
                    print(f"Time elapsed: {time.time() - start}")
                return cost, path, len(path), len(visited)
    exit(1)


def ucs(initial_state: str, goal_states: set, state_dict: dict, *_):
    open_list = [(0, initial_state)]
    parent_dict = dict()
    total_cost_dict = dict()
    visited = set()

    while open_list:
        current_state_cost, current_state_name = heapq.heappop(open_list)
        visited.add(current_state_name)

        if current_state_name in goal_states:
            path, cost = backtrace(initial_state, current_state_name, parent_dict)
            if measure_time:
                print(f"Time elapsed: {time.time() - start}")
            return cost, path, len(path), len(visited)

        children = state_dict[current_state_name]

        for child_name, child_cost in children:
            if (
                child_name not in parent_dict
                or total_cost_dict[child_name] > current_state_cost + child_cost
            ) and child_name not in visited:
                parent_dict[child_name] = (current_state_name, child_cost)
                total_cost_dict[child_name] = child_cost + current_state_cost
                heapq.heappush(open_list, (child_cost + current_state_cost, child_name))
    exit(1)


def generate_heuristic_dict(heuristic_path: str):
    with open(heuristic_path, encoding="utf-8") as f:
        return {
            k: float(v)
            for k, v in [x.split(": ") for x in f.readlines() if x[0] != "#"]
        }


def astar(initial_state: str, goal_states: set, state_dict: dict, heuristic_path: str):
    heuristic_dict = generate_heuristic_dict(heuristic_path)

    open_list = [(0 + heuristic_dict[initial_state], initial_state)]
    parent_dict = dict()
    total_cost_dict = {initial_state: 0}
    visited = set()

    while open_list:
        current_state_cost, current_state_name = heapq.heappop(open_list)
        visited.add(current_state_name)

        if current_state_name in goal_states:
            path, cost = backtrace(initial_state, current_state_name, parent_dict)
            if measure_time:
                print(f"Time elapsed: {time.time() - start}")
            return cost, path, len(path), len(visited)

        children = state_dict[current_state_name]

        for child_name, child_cost in children:
            if child_name not in visited:
                g = total_cost_dict[current_state_name] + child_cost
                h = heuristic_dict[child_name]
                f = max(
                    total_cost_dict[current_state_name]
                    + heuristic_dict[current_state_name],
                    g + h,
                )

                if child_name not in total_cost_dict or g < total_cost_dict[child_name]:
                    total_cost_dict[child_name] = g
                    parent_dict[child_name] = (current_state_name, child_cost)
                    heapq.heappush(open_list, (f, child_name))
    exit(1)


def check_optimistic(goal_states, state_dict, heuristic_path):
    heuristic_dict = generate_heuristic_dict(heuristic_path)
    print(f"# HEURISTIC-OPTIMISTIC {heuristic_path}")
    optimistic = True

    for state in state_dict:
        real_cost, *_ = ucs(state, goal_states, state_dict)
        heuristic_cost = heuristic_dict[state]
        if heuristic_cost <= real_cost:
            print(
                f"[CONDITION]: [OK] h({state}) <= h*: {heuristic_cost} <= {real_cost}"
            )
        else:
            print(
                f"[CONDITION]: [ERR] h({state}) <= h*: {heuristic_cost} <= {real_cost}"
            )
            optimistic = False

    if optimistic:
        print("[CONCLUSION]: Heuristic is optimistic.")
    else:
        print("[CONCLUSION]: Heuristic is not optimistic.")


def check_consistent(state_dict, heuristic_path):
    heuristic_dict = generate_heuristic_dict(heuristic_path)
    print(f"# HEURISTIC-CONSISTENT {heuristic_path}")
    consistent = True
    for state, children in state_dict.items():
        for child_name, child_cost in children:
            heuristic_cost_parent = heuristic_dict[state]
            heuristic_cost_child = heuristic_dict[child_name]
            if heuristic_cost_parent <= child_cost + heuristic_cost_child:
                print(
                    f"[CONDITION]: [OK] h({state}) <= h({child_name}) + c: {heuristic_cost_parent} <= {heuristic_cost_child} + {child_cost}"
                )
            else:
                print(
                    f"[CONDITION]: [ERR] h({state}) <= h({child_name}) + c: {heuristic_cost_parent} <= {heuristic_cost_child} + {child_cost}"
                )
                consistent = False

    if consistent:
        print("[CONCLUSION]: Heuristic is consistent.")
    else:
        print("[CONCLUSION]: Heuristic is not consistent.")


def main():
    global measure_time
    parser = create_parser()
    args = parser.parse_args()
    measure_time = args.t

    if args.alg == "astar" and not args.h:
        parser.error("--alg astar requires --h heuristic_descriptor")

    initial_state, goal_states, state_dict = generate_state_dict(
        args.ss,
        sort_children=True if args.alg == "bfs" else False,
        sort_nodes=True if args.check_optimistic or args.check_consistent else False,
    )

    if args.check_consistent:
        check_consistent(state_dict, args.h)
    elif args.check_optimistic:
        check_optimistic(goal_states, state_dict, args.h)
    else:
        alg_dict = {"bfs": bfs, "ucs": ucs, "astar": astar}
        cost, path, path_len, num_visited = alg_dict[args.alg](
            initial_state, goal_states, state_dict, args.h
        )
        print_output(args.alg, "yes", num_visited, path_len, cost, path, args.h)


if __name__ == "__main__":
    main()
