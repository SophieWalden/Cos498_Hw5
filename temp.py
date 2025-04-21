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

for key, val in STRUCTURE_BLOCKS.items():
    width = len(val[0])

    padding = ["air"] * (width + 2)

    for row in val:
        row.append("air")
        row.insert(0, "air")

    val.insert(0, padding)    
    val.append(padding)
    print(f"'{key}': {val},")