
import copy

STRUCTURE_COSTS = {
    "spiral": {"blocks": 10},
    "cross": {"blocks": 5},
    "frame": {"blocks": 8},
    "dot": {"blocks": 1},
    "stairs": {"blocks": 6},
    "plus": {"blocks": 5},
    "corner": {"blocks": 3},
    "arrow": {"blocks": 6},
    "zigzag": {"blocks": 7},
    "diamond": {"blocks": 5}
}

STRUCTURE_BLOCKS = {
    "spiral": [
        ["air", "air", "air", "air", "air"],
        ["air", "block", "block", "block", "air"],
        ["air", "air", "air", "block", "air"],
        ["air", "block", "block", "block", "air"],
        ["air", "air", "air", "air", "air"]
    ],
    "cross": [
        ["air", "block", "air"],
        ["block", "block", "block"],
        ["air", "block", "air"]
    ],
    "frame": [
        ["block", "block", "block"],
        ["block", "air", "block"],
        ["block", "block", "block"]
    ],
    "dot": [
        ["block"]
    ],
    "stairs": [
        ["block", "air", "air"],
        ["air", "block", "air"],
        ["air", "air", "block"]
    ],
    "plus": [
        ["air", "block", "air"],
        ["block", "block", "block"],
        ["air", "block", "air"]
    ],
    "corner": [
        ["block", "block"],
        ["block", "air"]
    ],
    "arrow": [
        ["air", "block", "air"],
        ["block", "block", "block"],
        ["air", "block", "air"]
    ],
    "zigzag": [
        ["block", "air", "block", "air"],
        ["air", "block", "air", "block"]
    ],
    "diamond": [
        ["air", "block", "air"],
        ["block", "air", "block"],
        ["air", "block", "air"]
    ]
}



class Structure:
    def __init__(self, type, blocks=None):
        self.type = type

        if type == "custom":
            self.cost = {"blocks": 0}
            self.actions = blocks
        else:
            self.cost = STRUCTURE_COSTS[type]
            self.actions = copy.deepcopy(STRUCTURE_BLOCKS[type])
    
