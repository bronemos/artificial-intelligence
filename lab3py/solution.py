import sys
from math import log2
from collections import Counter, defaultdict
from copy import deepcopy
from typing import List


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


def dfs_print_tree(root: Node, depth=1, path=""):
    if root.child_dict is None:
        print(path + f"{root.x}")
        return
    for value, child in root.child_dict.items():
        dfs_print_tree(child, depth=depth + 1, path=path + f"{depth}:{root.x}={value} ")


class ID3:
    def __init__(self, depth=None, verbose=False):
        self.__verbose = verbose
        self.__root: Node = None

    def __validation_print(self, features: List, entropies: List):
        print(
            " ".join(
                [
                    f"IG({feature})={entropy:.4f}"
                    for feature, entropy in zip(features, entropies)
                ]
            )
        )

    def __calculate_entropy(self, outcomes: List[int]):
        return -sum(
            [
                float(x) / sum(outcomes) * log2(float(x) / sum(outcomes))
                for x in outcomes
            ]
        )

    def __filter_by_v(self, d: dict, y: str, v: str):
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

    def __ig(self, d: dict, x: str):
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

    def __id3(self, d: dict, d_parent: dict, features: List, y: List):
        if len(d) == 1:
            v = sorted(Counter(d_parent[y]).most_common(), key=lambda x: (x[1], x[0]))[
                0
            ][0]
            return Node(v, v)
        v = sorted(Counter(d[y]).most_common(), key=lambda x: (x[1], x[0]))[0][0]
        d_yv = self.__filter_by_v(d, y, v)
        if len(features) == 1 or d == d_yv:
            return Node(v, v)
        entropies = [self.__ig(d, x) for x in features[:-1]]

        if self.__verbose:
            self.__validation_print(features[:-1], entropies)

        max_entropy = max(entropies)
        max_index = entropies.index(max_entropy)
        x = features[max_index]
        subtrees = dict()
        for value in set(d[x]):
            d_xv = self.__filter_by_v(d, x, value)
            d_copy = deepcopy(d)
            d_copy.pop(x)
            d_xv.pop(x)
            feautres_next = deepcopy(features)
            feautres_next.remove(x)
            t = self.__id3(d_xv, d_copy, feautres_next, y)
            subtrees[value] = t
        return Node(x, v, subtrees)

    def print_tree(self):
        dfs_print_tree(self.__root)

    def fit(self, train_dataset: dict):
        self.__root = self.__id3(
            train_dataset,
            train_dataset,
            list(train_dataset.keys()),
            list(train_dataset.keys())[-1],
        )

    def predict(self, test_dataset: dict):
        predictions = list()
        for test_no in range(len(test_dataset[list(test_dataset.keys())[-1]])):
            curr_node = self.__root
            while curr_node.child_dict is not None:
                curr_node = curr_node.child_dict[test_dataset[curr_node.x][test_no]]
                if type(curr_node) == str:
                    break
            if type(curr_node) == str:
                predictions.append(curr_node)
            else:
                predictions.append(curr_node.x)
        print(f"[PREDICTIONS]: {' '.join(predictions)}")


def load_data(train_path, test_path):
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
    model = ID3(verbose=True)
    model.fit(train_dataset)
    model.print_tree()
    model.predict(test_dataset)


if __name__ == "__main__":
    main()
