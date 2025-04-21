
import copy

STRUCTURE_COSTS = {
    "pillar": {"blocks": 12},
    "archway": {"blocks": 9},
    "column_frame": {"blocks": 12},
    "circle_base": {"blocks": 12},
    "spire": {"blocks": 12},
    "frame_with_pillars": {"blocks": 15},
    "diamond_pillar": {"blocks": 12},
    "temple_entrance": {"blocks": 12},
    "hexagonal_frame": {"blocks": 13},
    "inverted_pyramid": {"blocks": 12},
    "spiral": {"blocks": 10}
}

STRUCTURE_BLOCKS = {
    'pillar': [
        ['air', 'air', 'air', 'air', 'air', 'air', 'air'],
        ['air', 'air', 'block', 'air', 'air', 'air', 'air'],
        ['air', 'block', 'block', 'block', 'block', 'air', 'air'],
        ['air', 'air', 'block', 'air', 'air', 'air', 'air'],
        ['air', 'air', 'air', 'air', 'air', 'air', 'air']
    ],
    
    'archway': [
        ['air', 'air', 'block', 'air', 'air'],
        ['air', 'block', 'air', 'block', 'air'],
        ['block', 'air', 'block', 'air', 'block'],
        ['air', 'block', 'air', 'block', 'air'],
        ['air', 'air', 'block', 'air', 'air']
    ],
    
    'column_frame': [
        ['air', 'air', 'block', 'air', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block'],
        ['air', 'block', 'block', 'block', 'air'],
        ['air', 'air', 'block', 'air', 'air']
    ],
    
    'circle_base': [
        ['air', 'air', 'block', 'air', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block'],
        ['air', 'block', 'block', 'block', 'air'],
        ['air', 'air', 'block', 'air', 'air']
    ],
    
    'spire': [
        ['air', 'air', 'block', 'air', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block']
    ],
    
    'frame_with_pillars': [
        ['air', 'air', 'block', 'air', 'air', 'block', 'air'],
        ['air', 'block', 'block', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block', 'block', 'block'],
        ['air', 'block', 'block', 'block', 'block', 'block', 'air'],
        ['air', 'air', 'block', 'air', 'air', 'block', 'air']
    ],
    
    'diamond_pillar': [
        ['air', 'air', 'block', 'air', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block'],
        ['air', 'block', 'block', 'block', 'air'],
        ['air', 'air', 'block', 'air', 'air']
    ],
    
    'temple_entrance': [
        ['air', 'air', 'block', 'air', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block'],
        ['air', 'block', 'block', 'block', 'air'],
        ['air', 'air', 'block', 'air', 'air']
    ],
    
    'hexagonal_frame': [
        ['air', 'air', 'block', 'air', 'air', 'block'],
        ['air', 'block', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block', 'block'],
        ['air', 'block', 'block', 'block', 'block', 'air'],
        ['air', 'air', 'block', 'air', 'air', 'block']
    ],
    
    'inverted_pyramid': [
        ['air', 'air', 'air', 'air', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['air', 'block', 'block', 'block', 'air'],
        ['block', 'block', 'block', 'block', 'block'],
        ['air', 'air', 'air', 'air', 'air']
    ],

    'spiral': [
        ['air', 'air', 'air', 'air', 'air', 'air', 'air'],
        ['air', 'air', 'air', 'air', 'air', 'air', 'air'],
        ['air', 'air', 'block', 'block', 'block', 'air', 'air'],
        ['air', 'air', 'air', 'air', 'block', 'air', 'air'],
        ['air', 'air', 'block', 'block', 'block', 'air', 'air'],
        ['air', 'air', 'air', 'air', 'air', 'air', 'air'],
        ['air', 'air', 'air', 'air', 'air', 'air', 'air']
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
    
