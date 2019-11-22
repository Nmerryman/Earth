import tkinter as tk
import time
import win32ui
import pyautogui as pag
import numpy as np
from numpy import array
import random

pag.PAUSE = 0.0
target_site = 'Jstris - Mozilla Firefox (Private Browsing)'
test_target = 'Jstris - Mozilla Firefox'

window_name = test_target


# 6:Z, 7:S, 1:I, 2:O, 3:L, 4:J, 5:T
#


# only the field cords
def get_cords():
    def append_cords(data):
        # only need TL and BR corners
        corners.append((data.x, data.y))
        print(corners)
        if len(corners) == 2:
            time.sleep(.2)
            root.destroy()
        print(data.x, data.y)

    def key(given_key):
        # stop program when press esc
        if given_key.keycode == 27:
            root.destroy()
        print(given_key)

    corners = []
    queue_size = []
    root = tk.Tk()
    root.title('test')
    root.attributes('-alpha', .5)
    s_width = root.winfo_screenwidth()
    s_height = root.winfo_screenheight()
    root.overrideredirect(True)
    root.geometry(f'{s_width}x{s_height}+0+0')
    root.bind('<Key>', key)
    root.bind('<Button 1>', append_cords)
    root.mainloop()
    delta_x = (corners[1][0] - corners[0][0]) / 9
    delta_y = (corners[1][1] - corners[0][1]) / 19
    # print(delta_x, delta_y)
    real_cords = []
    for a in range(20):
        hold = []
        for b in range(10):
            hold.append((int(corners[0][0] + b * delta_x), int(corners[0][1] + a * delta_y)))
        real_cords.append(hold)
    return real_cords


# to clean up the main function
def get_cord_wrapper(use_past_cords=False):
    queue_cords = []
    if use_past_cords:
        file = open('Cords_Cypher.txt', 'r')
        hold = file.read()
        cords = eval(hold)
    else:
        cords = get_cords()
        file = open('Cords_Cypher.txt', 'w')
        file.write(str(cords))
        file.close()
    delta_x = cords[0][1][0] - cords[0][0][0]
    for a in cords:
        queue_cords.append((a[-1][0] + 3 * delta_x, a[0][1]))
    return cords, queue_cords


# return the heights, holes, and maybe others
def get_field(cords):
    global window_name
    w = win32ui.FindWindow(None, window_name)
    color_map = []
    for a in cords:
        hold = []
        for place, data in enumerate(a):
            dc = w.GetWindowDC()
            val = dc.GetPixel(data[0], data[1])
            dc.DeleteDC()
            hold.append(color_to_name(val))
        color_map.append(hold)
    return color_map


def get_queue(queue_cords):
    global window_name
    map_colors = []
    order = []
    w = win32ui.FindWindow(None, window_name)
    for data in queue_cords:
        dc = w.GetWindowDC()
        val = dc.GetPixel(data[0], data[1])
        dc.DeleteDC()
        order.append(color_to_name(val))
    ready = True
    for a in map_colors:
        if ready and a is not 0:
            ready = False
            order.append(a)
        else:
            ready = True
    return order


# used in get_field()
def color_to_name(color):
    names = {0: 0, 3608535: 6, 9054639: 5, 154595: 3, 12992801: 4,
             110937: 7, 14129935: 1, 172003: 2}
    try:
        give = names[color]
    except KeyError:
        # give = color
        give = 0
    return give


def get_heights(color_map):
    heights = np.zeros((10,))
    for a in range(10):
        # todo check to make sure the stop is at a good value
        stop = 19
        caught = False
        for b in range(2, 19):
            if color_map[b + 1][a] != 0 and not caught:
                stop = b
                caught = True
        heights.itemset(a, 19 - stop)
    return heights


def hard_drop(active_piece, offset, heights):
    # todo clean up comments
    # format will be rotations, direction of moves, moves -> '1+3'
    store = []
    center = eval('4' + offset[1:])
    # had to place str(int()) when ever there was height compensation
    if active_piece == 6:
        if offset[0] == '0':
            # -1 to compensate the shape
            # range: -3, 4
            store.append(int(heights[center - 1]) - 1)
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]))
        else:
            # range: -4, 4
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]) - 1)
    elif active_piece == 7:
        if offset[0] == '0':
            # -1 to compensate the shape
            # range: -3, 4
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]) - 1)
        else:
            # range: -4, 4
            store.append(int(heights[center]) - 1)
            store.append(int(heights[center + 1]))
    elif active_piece == 2:
        # no rotations possible
        # range: -4, 4
        store.append(int(heights[center]))
        store.append(int(heights[center + 1]))
    elif active_piece == 1:
        if offset[0] == '0':
            # range: -3, 3
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]))
            store.append(int(heights[center + 2]))
        else:
            # range: -5, 4
            center += 1
            store.append(int(heights[center]))
    elif active_piece == 3:
        if offset[0] == '0':
            # range: -3, 4
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]))
        elif offset[0] == '1':
            # range: -4, 4
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]))
        elif offset[0] == '2':
            # range: -3, 4
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]) - 1)
            store.append(int(heights[center + 1]) - 1)
        elif offset[0] == '3':
            # range: -4, 4
            store.append(int(heights[center - 1]) - 2)
            store.append(int(heights[center]))
    elif active_piece == 4:
        # offset is weird because of copy and paste
        if offset[0] == '0':
            # range: -3, 4
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]))
        elif offset[0] == '1':
            # range: -4, 4
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]) - 2)
        elif offset[0] == '2':
            # range: -3, 4
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]) + 1)
        elif offset[0] == '3':
            # range: -4, 4
            store.append(int(heights[center]))
            store.append(int(heights[center - 1]))
    else:
        if offset[0] == '0':
            # range: -3, 4
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]))
        elif offset[0] == '1':
            # range: -4, 4
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]) - 1)
        elif offset[0] == '2':
            # range: -3, 4
            store.append(int(heights[center - 1]) - 1)
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]) - 1)
        else:
            # range: -3, 5
            store.append(int(heights[center - 1]) - 1)
            store.append(int(heights[center]))

    # after compensating height, get total missing under line
    # todo abs the values
    # store2 = []
    cost = 0
    for a in store:
        cost += max(store) - a
    # cost = max(store2) * len(store)
    # for a in store2:
    #     store3 = abs(a - max(store2))
    # print('end of hard', store, cost, offset, heights)
    # new_heights = new_height_map(active_piece, offset, heights)
    if active_piece == 4 or active_piece == 3:
        print(99, offset, cost, store, heights)
    return cost, min(store), center


def get_wells(heights, tipping=3):
    # todo change if well check needs to happen on other side of pieces
    prev = 99
    # tipping = 3
    locations = []
    for num, a in enumerate(heights):
        if num is not 9:
            if prev - a > tipping and heights[num + 1] - a > tipping:
                locations.append(num)
            prev = a
        else:
            if prev - a > tipping:
                locations.append(num)
    return locations


def filter_options(options):

    def use_std(options_in, thresh_hold=1, last_out=False):
        # gets best std with 1 out
        if last_out:
            lowest_std = 99
            use = 0
            # base use lowest std
            for num_a, a in enumerate(options_in):
                # print('num_a:', num_a, 'a:', a)
                # print('std:', a[9])
                if a[9] < lowest_std:
                    lowest_std = a[9]
                    use = num_a
            return options_in[use]
        else:
            options_out = []
            for a in options_in:
                if a[9] < thresh_hold:
                    options_out.append(a)
            if len(options_out) == 0:
                options_out = use_std(options_in, thresh_hold, True)
                print('out nothing', len(options_in))
            return options_out

    def lowest_avg(options_in, similarity_thresh_hold=1, last_out=False):
        hold = []
        options_out = []
        if not last_out:
            for a in options_in:
                hold.append(a[8])
            lowest = min(hold) + similarity_thresh_hold
            for a in options_in:
                if a[8] < lowest:
                    options_out.append(a)
            return options_out
        lowest_avg = 99
        for a in options_in:
            selected = a[8]
            if selected < lowest_avg:
                lowest_avg = selected
                options_out.append(a)
        return options_out

    def lowest_hole_count_final(options_in):
        lowest_hole_count = 99
        for a in options_in:
            if a[13] < lowest_hole_count:
                options_out = a
                lowest_hole_count = a[13]
        return options_out

    # options_format: [active_piece, offset, color_map, queue]
    # must return offset
    for num_a, a in enumerate(options):
        returned_map_vals = map_scan(a[2], a[1])
        for b in returned_map_vals:
            options[num_a].append(b)
    # options_format: [active_piece, offset, color_map, queue, lines_cleared, new_map, new_height_array, wells,
    # height_avg, height_std, first_hole_heights, hole_locations, hole_diff_from_surface, hole_count

    pipe = lowest_avg(options)
    print(len(options), len(pipe), 'pipe:', pipe)
    pipe = use_std(pipe, last_out=True)
    # pipe = random.choice(pipe)
    print(pipe)
    pipe = lowest_hole_count_final(options)
    return pipe[1]


def sim_drop_map(colormap, active, offset):
    for num_a in range(len(colormap[0])):
        colormap[0][num_a] = 0
    physical_shapes = {1: array(((0, 0, 0, 0),
                                 (1, 1, 1, 1),
                                 (0, 0, 0, 0),
                                 (0, 0, 0, 0))),
                       2: array(((0, 1, 1),
                                 (0, 1, 1),
                                 (0, 0, 0))),
                       3: array(((0, 0, 1),
                                 (1, 1, 1),
                                 (0, 0, 0))),
                       4: array(((1, 0, 0),
                                 (1, 1, 1),
                                 (0, 0, 0))),
                       5: array(((0, 1, 0),
                                 (1, 1, 1),
                                 (0, 0, 0))),
                       6: array(((1, 1, 0),
                                 (0, 1, 1),
                                 (0, 0, 0))),
                       7: array(((0, 1, 1),
                                 (1, 1, 0),
                                 (0, 0, 0)))
                       }
    active_shape = np.rot90(physical_shapes[active], 4 - int(offset[0]))
    center_found = False
    left_pad_bonus, bottom_pad_bonus, right_pad_bonus, top_pad_bonus = 0, 0, 0, 0
    for a in active_shape.sum(0):
        if not center_found and a == 0:
            # print('left bonus')
            left_pad_bonus += 1
        elif center_found and a == 0:
            # print('increment right bonus')
            right_pad_bonus += 1
        else:
            center_found = True
    center_found = False
    for a in active_shape.sum(1):
        if not center_found and a == 0:
            # print('top bonus')
            top_pad_bonus += 1
        elif center_found and a == 0:
            # print('bottom bonus')
            bottom_pad_bonus += 1
        else:
            center_found = True
    if bottom_pad_bonus == 0:
        bottom_pad_bonus = -active_shape.shape[0]
    if right_pad_bonus == 0:
        right_pad_bonus = -active_shape.shape[1]
    clean_active_shape = active_shape[top_pad_bonus:-bottom_pad_bonus, left_pad_bonus:-right_pad_bonus]
    # start is on row=4 default is 3w
    left_pad = 3 + left_pad_bonus + int(offset[1:])
    right_pad = 10 - left_pad - clean_active_shape.shape[1]
    bottom_pad = 16
    top_pad = 20 - bottom_pad - clean_active_shape.shape[0]
    # print('tb, t, bb, b, lb, l, rb, r:', top_pad_bonus, top_pad, bottom_pad_bonus, bottom_pad, left_pad_bonus, left_pad, right_pad_bonus, right_pad)
    mirror_test = clean_active_shape.copy()
    mirror_test -= 1
    mirror_test *= -1
    real_field = array(colormap)
    new_layer = np.pad(mirror_test, ((top_pad, bottom_pad), (left_pad, right_pad)), mode='constant',
                       constant_values=(1, 1))
    test_field = real_field * new_layer
    while np.array_equiv(real_field, test_field) and bottom_pad != 0:
        # print(real_field)
        # print('is')
        # print(test_field)
        # print('via \n', new_layer)
        bottom_pad -= 1
        top_pad = 20 - bottom_pad - clean_active_shape.shape[0]
        # print(bottom_pad, top_pad)
        new_layer = np.pad(mirror_test, ((top_pad, bottom_pad), (left_pad, right_pad)), mode='constant',
                           constant_values=(1, 1))
        test_field = real_field * new_layer
    bottom_pad += 1
    if np.array_equiv(real_field, test_field) and bottom_pad == 1:
        bottom_pad -= 1
    top_pad = 20 - bottom_pad - clean_active_shape.shape[0]
    new_out_layer = real_field + np.pad(clean_active_shape, ((top_pad, bottom_pad), (left_pad, right_pad)),
                                        mode='constant', constant_values=(0, 0))
    # print('out: \n', new_out_layer)
    return new_out_layer.tolist()


def map_scan(color_map, offset):
    # from image I want to return: height array, wells, avg and/or std, lines cleared, new map for cleared lines,
    # holes, difference between heighest hole and surface
    lines_cleared, new_map = clear_lines(color_map)
    height_array = get_heights(new_map)
    wells = get_wells(height_array, 4)
    height_avg = height_array.sum() / len(height_array)
    height_std = height_array.std()
    first_holes_heights, hole_locations, total_holes = get_holes(color_map, height_array)
    # fixme hole stuff removed
    hole_diff = 0
    # hole_diff = height_array - array(first_holes_heights[:, 0])
    return lines_cleared, new_map, height_array.tolist(), wells, height_avg, height_std, first_holes_heights, \
           hole_locations, hole_diff, total_holes


def clear_lines(color_map):
    lines_cleared = 0
    lines_to_clear = []
    new_map = array(color_map)
    for num_a, a in enumerate(new_map):
        if a.prod() != 0:
            lines_to_clear.append(num_a)
    lines_cleared = len(lines_to_clear)
    for a in reversed(lines_to_clear):
        np.delete(new_map, a, 0)
    for _ in range(lines_cleared):
        np.insert(new_map, 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], axis=0)
    return lines_cleared, new_map.tolist()


def get_holes(color_map, height_array):
    hole_heights_by_column = []
    first_hole_list = []
    total_holes = 0
    # print('vv')
    # print('height_array:', height_array)
    for num_a, a in enumerate(height_array):
        first_found = False
        hole_heights = []
        a = int(a)
        for b in range(20 - a, 20):
            # fixme hole stuff
            if color_map[b][num_a] == 0:
                if not first_found:
                    first_found = True
                    first_hole_list.append((20 - b, num_a))
                hole_heights.append(b)
                total_holes += 1
            # print('holes, b, a, val:', total_holes, b, a, color_map[b][a])
        hole_heights_by_column.append(hole_heights)
    # print('column_heights:', hole_heights_by_column)
    # print('total:', total_holes)
    # print('first_list:', first_hole_list)
    # print('^^')
    return first_hole_list, hole_heights_by_column, total_holes


# todo this
def sim_map(color_map, active, offset, heights):
    # todo get usable piece and rotate (consider moving this outside to avoid continuously defining it.
    physical_shapes = {1: array(((0, 0, 0, 0),
                                 (1, 1, 1, 1),
                                 (0, 0, 0, 0),
                                 (0, 0, 0, 0))),
                       2: array(((0, 1, 1),
                                 (0, 1, 1),
                                 (0, 0, 0))),
                       3: array(((0, 0, 1),
                                 (1, 1, 1),
                                 (0, 0, 0))),
                       4: array(((1, 0, 0),
                                 (1, 1, 1),
                                 (0, 0, 0))),
                       5: array(((0, 1, 0),
                                 (1, 1, 1),
                                 (0, 0, 0))),
                       6: array(((1, 1, 0),
                                 (0, 1, 1),
                                 (0, 0, 0))),
                       7: array(((0, 1, 1),
                                 (0, 1, 1),
                                 (0, 0, 0)))
                       }
    active_shape = np.rot90(physical_shapes[active], 4 - int(offset[0]))
    center = 4 + int(offset[1:])

    # todo optimization possible with getting height map from outside
    height_array = array(get_heights(color_map))
    delta = np.std(height_array)
    # todo set floor shapes for each active piece
    # will build system that scans up for contact and build layer map list

    # todo get center height on location

    layer = []
    for _ in range(np.shape(active_shape)[1]):
        layer.append(10)
    for num_a, a in enumerate(np.flip(active_shape)):
        for num_b, b in enumerate(a):
            if layer[num_b] == 10 and b != 0:
                layer[num_b] = num_a
    floor = []
    # fix the shape
    # fixme error checking for o-piece needs to be removed
    if active == 2:
        floor = [10, 0, 0]
    else:
        for a in range(3):
            floor.append(layer[-3 + a])
    floor_array = array(floor)
    print('floor arrays, min:', floor_array, min(floor_array))
    floor_array -= min(floor_array)
    center_cords = [center, 0]
    # need to find center_cords[1]
    gaps = []
    for num_a, a in enumerate(floor):
        if a <= 5:
            gap_check_num = center - 1 + num_a
            gaps.append(height_array[gap_check_num] - a)
    center_cords[1] = max(gaps)
    active_base_shape = array(active_shape)
    bottom_pad = int(max((0, center_cords[1] - 1 - (active_base_shape.shape[0] - 3))))
    top_pad = 20 - active_base_shape.shape[0] - bottom_pad
    left_pad = max(0, center_cords[0] - 1 - (active_base_shape.shape[1] - 3))
    right_pad = 10 - active_base_shape.shape[1] - left_pad
    print('active:', active, 'pads:', top_pad, bottom_pad, left_pad, right_pad, 'gaps:', gaps)
    if bottom_pad != 0:
        print('center_cords, active_base_shape:', center_cords)
        print(active_base_shape)
    while active_base_shape.sum(1)[2] == 0:
        print('while situation', active_base_shape.sum(1)[2])
        active_base_shape = np.roll(active_base_shape, 1, axis=0)
        print('new:', active_base_shape)
    merge_piece = np.pad(active_base_shape, ((top_pad, bottom_pad), (left_pad, right_pad)), mode='constant',
                         constant_values=(0, 0))
    merge_field = array(color_map)
    out_field = merge_field + merge_piece
    print(out_field)
    pass


def cleaned_cypher_engine(color_map, queue_cords):
    possibilities = {6: [(-3, 5), (-4, 5)], 7: [(-3, 5), (-4, 5)], 2: [(-4, 5)],
                     1: [(-3, 4), (-5, 5)], 3: [(-3, 5), (-4, 5), (-3, 5), (-3, 6)],
                     4: [(-3, 5), (-4, 5), (-3, 5), (-3, 6)], 5: [(-3, 5), (-4, 5), (-3, 5), (-3, 6)]}

    pipe = []
    active_piece = color_map[0][4]
    queue = get_queue(queue_cords)
    if active_piece == 0:
        print('sleeps', active_piece)
        time.sleep(.01)
        return 1
    height_array = get_heights(color_map)
    wells = get_wells(height_array)
    # cycle through rotations
    for a, b in enumerate(possibilities[active_piece]):
        for c in range(b[0], b[1]):
            print('---------')
            # cycle through the possible offsets
            offset = f'{a}{c}'
            if len(offset) == 2:
                offset = offset[0] + '+' + offset[1]
            # get cost and compare to other costs from this offset
            # get all interesting info
            # what do I want possible to filter by:
            # space underneath, lowest piece, active piece, height deviation, line clears,
            # remove wells, open mini wells, create the smallest holes
            # will need: cost_space, lowest point, center of tile, height_map, active_piece
            print('offset', offset)
            returned_map = sim_drop_map(color_map, active_piece, offset)
            # print(returned_map)
            pipe.append([active_piece, offset, returned_map, queue])
    best = filter_options(pipe)
    print('placed', best, active_piece, wells)
    # time.sleep(.04)
    execute_offset(best)
    return 0


def cypher_engine(color_map, queue_cords):
    # todo removed tile_map and holes
    possibilities = {6: [(-3, 5), (-4, 5)], 7: [(-3, 5), (-4, 5)], 2: [(-4, 5)],
                     1: [(-3, 3), (-5, 5)], 3: [(-3, 5), (-4, 5), (-3, 5), (-3, 6)],
                     4: [(-3, 5), (-4, 5), (-3, 5), (-3, 5)], 5: [(-3, 5), (-4, 5), (-3, 5), (-3, 5)]}
    # set bad starting values

    score = 999999
    options_pipe = []
    pipe = []
    active_piece = color_map[0][4]
    count = 0
    queue = get_queue(queue_cords)
    if active_piece == 0:
        print('sleeps', active_piece)
        time.sleep(.01)
        return 1
    height_array = get_heights(color_map)
    wells = get_wells(height_array)
    # cycle through rotations
    for a, b in enumerate(possibilities[active_piece]):
        for c in range(b[0], b[1]):
            print('---------')
            # cycle through the possible offsets
            offset = f'{a}{c}'
            # add the + to the pos ones
            if len(offset) == 2:
                offset = offset[0] + '+' + offset[1]
            # get cost and compare to other costs from this offset
            # get all interesting info
            # what do I want possible to filter by:
            # space underneath, lowest piece, active piece, height deviation, line clears,
            # remove wells, open mini wells, create the smallest holes
            # will need: cost_space, lowest point, center of tile, height_map, active_piece
            # todo piece sim to update height map and line clear checker
            cost, low, center = hard_drop(active_piece, offset, height_array)
            # time.sleep(.25)
            print('offset', offset)
            returned_map = sim_drop_map(color_map, active_piece, offset)
            print(returned_map)
            pipe.append([active_piece, offset, color_map, queue])
            # sim_map(color_map, active_piece, offset, height_array)
            # print(cost)
            # restart list with best possible costs
            height_limit = 20
            if len(wells) > 0 and (
                    (active_piece == 3 and offset[0] == '3') or (active_piece == 4 and offset[0] == '1')):
                if wells.__contains__(center) and not queue[0:5].__contains__(1):
                    cost -= 5
                    if cost < 0:
                        cost = 0
                    print('discounted')
            # todo filter in a more robust system
            if cost < score and low < height_limit:
                options_pipe, score = [], cost
                options_pipe.append((cost, offset, low))
            # allow for multiple possible offsets
            elif cost == score and low < height_limit:
                options_pipe.append((cost, offset, low))
    best, lowest = '', 20
    print(options_pipe)
    for a in options_pipe:
        if a[2] < lowest:
            lowest = a[2]
            best = a[1]
    if active_piece == 5:
        for a in options_pipe:
            if a[1][0] == '2':
                best = a[1]
    print('placed', best, active_piece, wells)
    execute_offset(best)
    return 0


def execute_offset(offset):
    # rotations
    pag.press('q', presses=int(offset[0]))
    if offset[1] == '+':
        pag.press('right', presses=int(offset[2]))
    else:
        pag.press('left', presses=int(offset[2]))
    pag.press('space')
    # max is .04
    time.sleep(.04)


if __name__ == '__main__':
    # True if using saved cords
    cord_map, queue_map = get_cord_wrapper(True)
    input('Ready!>')
    time.sleep(2)
    pag.press('f4')
    time.sleep(1.9)
    end = 0
    while True:
        field_map = get_field(cord_map)
        # print(get_heights(field_map))
        # for hold_row in field_map:
        #     print(hold_row)
        # time.sleep(.5)
        # todo make use of queue
        error = cleaned_cypher_engine(field_map, queue_map)
        if error == 0:
            end = 0
        else:
            end += 1
        if end > 10:
            print('Game Over')
            breakpoint()
