neighbors = [
        ((0, 1), "LEFT"),
        ((1, 1), "RIGHT"),
        ((1, 0), 'UP'),
        ((0, 0), 'DOWN')
    ]

for neighbor in neighbors:
    tile, direction = neighbor
    print(tile, direction)