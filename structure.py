
def spiralStructure():
    actions = []

    descending = True
    for j in range(10):
        for i in range(10):
            actions.append(("move", (0, [1, -1][descending])))
            actions.append(("break", None))
        descending = not descending
        actions.append(("move", (1, 0)))

    actions.append(("move", (-5, -5)))
    directions = [[-1, 0], [0, 1], [1, 0], [0, -1]]
    for i in range(4, 14):
        move = directions[i % 4][:]
        move[0] *= i // 4
        move[1] *= i // 4

        actions.append(("move", move))
        actions.append(("place", None))
        actions.append(("move", [-item for item in move]))

    return actions


STRUCTURE_COSTS = {"spiral": {"blocks": 10}}
STRUCTURE_ACTIONS = {"spiral": spiralStructure()}



class Structure:
    def __init__(self, type):
        self.type = type
        self.cost = STRUCTURE_COSTS[type]
        self.actions = STRUCTURE_ACTIONS[type][:]
    
