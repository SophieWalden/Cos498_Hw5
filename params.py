FPS = 120
TILE_SIZE = 32

BOARD_WIDTH = 500
BOARD_HEIGHT = 200

AGENT_COUNTS = {"normal": 10, "copier": 2, "gravity": 15, "siphon": 2, "painter": 5}

# Certain agents can paint blocks
BLOCK_COLORS = [    
    "white",
    "gray",
    "black",
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink",
    "brown",
    "cyan",
    "magenta",
]

AGENT_COLORS = {"normal": (0, 0, 139), "copier": (180, 180, 0), "gravity": (180, 0, 0), "siphon": (230, 140, 0), "painter": (219,112,147)}
AGENT_IMAGES = {"normal": "structure_sprite", "copier": "copier_sprite", "gravity": "gravity_sprite", "siphon": "siphon_sprite", "painter": "painter_sprite"}