import numpy as np
from numpy import array

test_map = '''[[0 0 0 0 0 0 0 0 0 0]
 [1 1 0 0 0 0 0 0 0 0]
 [1 1 0 0 0 0 0 0 0 0]
 [0 7 0 0 0 0 0 0 0 0]
 [0 7 7 0 0 0 0 0 0 0]
 [0 1 7 5 0 0 0 0 7 0]
 [0 1 5 5 5 0 0 0 7 7]
 [0 1 3 2 2 0 4 4 4 7]
 [1 1 3 2 2 6 3 7 4 0]
 [1 4 3 3 6 6 3 7 7 0]
 [1 4 4 4 6 6 3 3 7 0]
 [1 6 4 4 6 6 2 2 0 0]
 [6 6 4 3 6 3 2 2 0 5]
 [6 7 4 3 0 3 0 5 5 5]
 [1 1 3 3 3 4 2 2 0 5]
 [1 1 7 6 6 0 6 6 5 5]
 [4 4 0 4 7 7 1 5 6 3]
 [4 7 3 3 5 7 1 5 5 2]
 [4 7 7 3 5 5 1 5 3 2]
 [2 2 7 3 5 6 6 0 3 0]]'''
a = test_map.replace(' ', ', ')
real_map = eval(a)
print(real_map)


def clear_lines(color_map):
    # print('checked for clear')
    # color_map = []
    lines_to_clear = []
    for num_a, a in enumerate(array(color_map)):
        if a.prod() != 0:
            # print('found line')
            lines_to_clear.append(num_a)
    lines_cleared = len(lines_to_clear)
    print('to clear', lines_to_clear)
    for a in reversed(lines_to_clear):
        color_map.pop(a)
    print('after deletions', color_map)
    for _ in range(lines_cleared):
        color_map.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    return lines_cleared, color_map

cleared, new = clear_lines(real_map)
print('cleared:', cleared)
print('new:')
print(array(new))
