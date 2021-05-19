import sys
import math
from collections import defaultdict


class Node:
    def __init__(self, x, children=None):
        self.x = x
        self.children = children


class ID3:
    def __init__(self, depth=None):
        self.root: Node = None

    def __ig():
        pass

    def __id3(self, train_dataset):
        pass

    def fit(self, train_dataset):
        self.root = self.__id3(train_dataset)

    def predict(self, test_dataset):
        pass


def load_data(train_path, test_path):
    with open(train_path, "r", encoding="utf-8") as f:
        lines = [x.strip().split(",") for x in f.readlines()]
        header = lines[0]
        data = lines[1:]
        train_dataset = dict()
        for column, feature_name in enumerate(header[:-1]):
            case_dict = defaultdict(lambda: defaultdict(lambda: 0))
            for case in data:
                case_dict[case[column]][case[-1]] += 1
            train_dataset[feature_name] = case_dict

        print(train_dataset)

    with open(test_path, "r", encoding="utf-8") as f:
        lines = [x.strip().split(",") for x in f.readlines()]
        header = lines[0]
        data = lines[1:]
        test_dataset = dict()

    return train_dataset, test_dataset


def main():
    train_dataset, test_dataset = load_data(sys.argv[1], sys.argv[2])
    model = ID3()
    model.fit(train_dataset)
    predictions = model.predict(test_dataset)


if __name__ == "__main__":
    main()
