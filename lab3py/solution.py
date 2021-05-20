import sys
from math import log2
from collections import Counter, defaultdict
from copy import deepcopy
from typing import List, Tuple, Dict


class Node:
    def __init__(self, x: str, most_common_value: str, children=None):
        self.__x = x
        if children is not None:
            self.__chil_dict = defaultdict(lambda: most_common_value)
            self.__chil_dict.update(children)
        else:
            self.__chil_dict = children

    @property
    def x(self) -> str:
        return self.__x

    @property
    def child_dict(self) -> dict:
        return self.__chil_dict


def dfs_print_tree(root: Node, depth=1, path="") -> None:
    if root.child_dict is None:
        print(path + f"{root.x}")
        return
    for value, child in root.child_dict.items():
        dfs_print_tree(child, depth=depth + 1, path=path + f"{depth}:{root.x}={value} ")


class ID3:
    def __init__(self, max_depth: int = -1, verbose: bool = False) -> None:
        self.__max_depth = max_depth
        self.__verbose = verbose
        self.__root: Node = None

    def __validation_print(self, features: List, entropies: List) -> None:
        print(
            " ".join(
                [
                    f"IG({feature})={entropy:.4f}"
                    for feature, entropy in zip(features, entropies)
                ]
            )
        )

    def __calculate_entropy(self, outcomes: List[int]) -> float:
        return -sum(
            [
                float(x) / sum(outcomes) * log2(float(x) / sum(outcomes))
                for x in outcomes
            ]
        )

    def __filter_by_v(self, d: dict, y: str, v: str) -> dict:
        return_d = deepcopy(d)
        to_remove = set()
        for key in return_d.keys():
            [
                to_remove.add(index)
                for index in range(len(return_d[key]))
                if return_d[y][index] != v
            ]
        for key in return_d.keys():
            return_d[key] = [
                el for index, el in enumerate(return_d[key]) if index not in to_remove
            ]
        return return_d

    def __ig(self, d: dict, x: str) -> float:
        outcomes = [count for _, count in Counter(d[list(d.keys())[-1]]).most_common()]
        init_dataset_entropy = self.__calculate_entropy(outcomes)
        outcomes_filtered = defaultdict(list)
        for index, value in enumerate(d[x]):
            outcomes_filtered[value].append(d[list(d.keys())[-1]][index])
        for key, value in outcomes_filtered.items():
            outcomes_filtered[key] = [
                count for _, count in Counter(value).most_common()
            ]
        expected_entropy = sum(
            [
                float(sum(outcome)) / sum(outcomes) * self.__calculate_entropy(outcome)
                if len(outcome) > 0
                else 0
                for outcome in outcomes_filtered.values()
            ]
        )
        return init_dataset_entropy - expected_entropy

    def __id3(
        self, d: dict, d_parent: dict, features: List, y: str, current_depth: int
    ) -> Node:
        if len(d) == 0:
            v = sorted(Counter(d_parent[y]).most_common(), key=lambda x: (-x[1], x[0]))[
                0
            ][0]
            return Node(v, v)
        v = sorted(Counter(d[y]).most_common(), key=lambda x: (-x[1], x[0]))[0][0]
        d_yv = self.__filter_by_v(d, y, v)
        if len(features) == 0 or d == d_yv or current_depth == self.__max_depth:
            return Node(v, v)
        entropies = [self.__ig(d, x) for x in features]

        if self.__verbose:
            self.__validation_print(features, entropies)

        max_entropy = max(entropies)
        max_index = entropies.index(max_entropy)
        x = features[max_index]
        subtrees = dict()
        for value in set(d[x]):
            d_xv = self.__filter_by_v(d, x, value)
            d_copy = deepcopy(d)
            d_xv.pop(x)
            feautres_next = deepcopy(features)
            feautres_next.remove(x)
            t = self.__id3(d_xv, d_copy, feautres_next, y, current_depth + 1)
            subtrees[value] = t
        return Node(x, v, subtrees)

    def print_tree(self) -> None:
        print("[BRANCHES]:")
        dfs_print_tree(self.__root)

    def fit(self, train_dataset: dict) -> None:
        self.__root = self.__id3(
            train_dataset,
            train_dataset,
            sorted(list(train_dataset.keys())[:-1]),
            list(train_dataset.keys())[-1],
            0,
        )

    def predict(self, test_dataset: dict) -> None:
        predictions = list()
        goal_column = list(test_dataset.keys())[-1]
        for test_no in range(len(test_dataset[goal_column])):
            curr_node = self.__root
            while type(curr_node) != str and curr_node.child_dict is not None:
                curr_node = curr_node.child_dict[test_dataset[curr_node.x][test_no]]
            predictions.append(curr_node if type(curr_node) == str else curr_node.x)
        print(f"[PREDICTIONS]: {' '.join(predictions)}")
        print(
            f"[ACCURACY]: {float(sum([1 for predicted, correct in zip(predictions, test_dataset[goal_column]) if predicted == correct]))/len(predictions):.5f}"
        )

        classes = sorted(set(predictions) | set(test_dataset[goal_column]))
        cm_dim = len(set(predictions) | set(test_dataset[goal_column]))
        confusion_matrix = [[0 for _ in range(cm_dim)] for _ in range(cm_dim)]
        for predicted, correct in zip(predictions, test_dataset[goal_column]):
            confusion_matrix[classes.index(correct)][classes.index(predicted)] += 1
        confusion_matrix_str = "\n".join(
            [
                " ".join([str(confusion_matrix[y][x]) for x in range(cm_dim)])
                for y in range(cm_dim)
            ]
        )
        print(f"[CONFUSION_MATRIX]:\n{confusion_matrix_str}")


def load_data(train_path: str, test_path: str) -> Tuple[Dict]:
    with open(train_path, "r", encoding="utf-8") as f:
        lines = [x.strip().split(",") for x in f.readlines()]
        train_dataset = dict()
        for index, feature in enumerate(lines[0]):
            train_dataset[feature] = [x[index] for x in lines[1:]]

    with open(test_path, "r", encoding="utf-8") as f:
        lines = [x.strip().split(",") for x in f.readlines()]
        test_dataset = dict()
        for index, feature in enumerate(lines[0]):
            test_dataset[feature] = [x[index] for x in lines[1:]]

    return train_dataset, test_dataset


def main():
    train_dataset, test_dataset = load_data(sys.argv[1], sys.argv[2])
    try:
        depth = int(sys.argv[3])
    except IndexError:
        depth = -1
    model = ID3(max_depth=depth, verbose=True)
    model.fit(train_dataset)
    model.print_tree()
    model.predict(test_dataset)


if __name__ == "__main__":
    main()
