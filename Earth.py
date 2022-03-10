import tkinter as tk
import time
import win32ui
import pyautogui as pag
import numpy as np
from numpy import array
import concurrent.futures
import random

# set up some initial values
pag.PAUSE = 0.0
target_site = 'Jstris - Mozilla Firefox (Private Browsing)'
test_target = 'Jstris - Mozilla Firefox'

window_name = target_site
if window_name == 'Jstris - Mozilla Firefox (Private Browsing)':
    right_key = 'up'
else:
    right_key = 'v'


# 6:Z, 7:S, 1:I, 2:O, 3:L, 4:J, 5:T
#


# open transparent and intractable window to find starting coordinates
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


# to clean up the coordinate function
# can use a cache
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


# interpret the given area to convert to board state
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


# get visible queue
def get_queue(queue_cords):
    global window_name
    map_colors = []
    order = []
    w = win32ui.FindWindow(None, window_name)
    for data in queue_cords:
        dc = w.GetWindowDC()
        val = dc.GetPixel(data[0], data[1])
        dc.DeleteDC()
        map_colors.append(color_to_name(val))
    ready = True
    for a in map_colors:
        if ready and a is not 0:
            ready = False
            order.append(a)
        else:
            ready = True
    return order


# used in get_field() as a color to piece conversion helper
def color_to_name(color):
    names = {0: 0, 3608535: 6, 9054639: 5, 154595: 3, 12992801: 4,
             110937: 7, 14129935: 1, 172003: 2}
    try:
        give = names[color]
    except KeyError:
        # give = color
        give = 0
    return give


# analyse board for height of each column
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


# analyse the board to evaluate columns of interest
def get_wells(heights, tipping=3):
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


# potential future states filter for the best ones
def filter_options(options, queue, current_depth, mid_scan=True):
    # return options[0][1]  # Debug to use first avalible option

    def pipe_check(pipe_in):
        temp = []
        if type(pipe_in[0]) != list:
            temp.append(pipe_in)
            return temp
        return pipe_in

    def use_std(options_in, thresh_hold=2, last_out=False):
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

    def lowest_hole_count_final(options_in, last_out=True):
        lowest_hole_count = 99
        options_out = []
        options_in = pipe_check(options_in)
        for a in options_in:
            if a[13] < lowest_hole_count:
                options_out = a
                lowest_hole_count = a[13]
            print('low count', lowest_hole_count)
        return options_out

    # options_format: [active_piece, offset, color_map, queue]
    # must return offset
    for num_a, a in enumerate(options):
        returned_map_vals = map_scan(a[2], a[1])
        for b in returned_map_vals:
            options[num_a].append(b)
    # options_format: [active_piece, offset, color_map, queue, 4:lines_cleared, new_map, new_height_array, wells,
    # 8:height_avg, height_std, first_hole_heights, hole_locations, 12:hole_diff_from_surface, hole_count]

    pipe = options
    min_cleared_hold = []
    for a in pipe:
        min_cleared_hold.append(a[4])
    temp_pipe = []
    # print('min_cleared_hold, max:', min_cleared_hold, max(min_cleared_hold))
    for a in pipe:
        if a[4] > 1:
            temp_pipe.append(a)
    if len(temp_pipe) == 0:
        temp_pipe = pipe
    pipe = temp_pipe
    pipe = pipe_check(pipe)
    pipe = lowest_avg(pipe, similarity_thresh_hold=2)
    pipe = pipe_check(pipe)
    print(len(options), len(pipe), 'pipe:', pipe)
    pipe = use_std(pipe, thresh_hold=2, last_out=False)
    # pipe = random.choice(pipe)
    print('last_step:', len(pipe))
    pipe = lowest_hole_count_final(pipe, last_out=False)
    return pipe[1]


# A basic simulation of the board to test possible moves
def sim_drop_map(colormap, active, offset):
    if len(colormap) == 21:
        colormap.pop()
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
    # fixme fix hole_diff (set to out of bounds to be ignored rn)
    hole_diff = 0
    # hole_diff = height_array - array(first_holes_heights[:, 0])
    return lines_cleared, new_map, height_array.tolist(), wells, height_avg, height_std, first_holes_heights, \
           hole_locations, hole_diff, total_holes


# account for clearing lines is simulations
def clear_lines(color_map):
    # print('checked for clear')
    # color_map = []
    lines_to_clear = []
    for num_a, a in enumerate(array(color_map)):
        if a.prod() != 0:
            # print('found line')
            lines_to_clear.append(num_a)
    lines_cleared = len(lines_to_clear)
    for a in reversed(lines_to_clear):
        color_map.pop(a)
    for _ in range(lines_cleared):
        color_map.insert(0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    return lines_cleared, color_map


# identify and sort buried holes
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
            # fixme improve hole stuff
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


# generate potential states to be evaluated
def hands_engine(color_map_in, current_level=0):
    possibilities = {6: [(-3, 5), (-4, 5)], 7: [(-3, 5), (-4, 5)], 2: [(-4, 5)],
                     1: [(-3, 4), (-5, 5)], 3: [(-3, 5), (-4, 5), (-3, 5), (-3, 6)],
                     4: [(-3, 5), (-4, 5), (-3, 5), (-3, 6)], 5: [(-3, 5), (-4, 5), (-3, 5), (-3, 6)]}

    print(color_map_in)
    color_map = color_map_in
    if current_level == 0:
        color_map = color_map_in[2]
    active_piece = color_map_in[-1]
    # print('active_piece:', active_piece)
    pipe = []
    # cycle through rotations
    for a, b in enumerate(possibilities[active_piece]):
        for c in range(b[0], b[1]):
            # cycle through the possible offsets
            offset = f'{a}{c}'
            if len(offset) == 2:
                offset = offset[0] + '+' + offset[1]
            # what do I want possible to filter by:
            # space underneath, lowest piece, active piece, height deviation, line clears,
            # remove wells, open mini wells, create the smallest holes
            # will need: cost_space, lowest point, center of tile, height_map, active_piece
            # print('offset', offset)
            returned_map = sim_drop_map(color_map, active_piece, offset)
            empty, returned_map = clear_lines(returned_map)
            # print(returned_map)
            pipe.append([active_piece, offset, returned_map])
    return pipe


# sends the chosen instructions to the game window
def execute_offset(offset):
    # rotations
    global right_key
    pag.press(right_key, presses=int(offset[0]))
    if offset[1] == '+':
        pag.press('right', presses=int(offset[2]))
    else:
        pag.press('left', presses=int(offset[2]))
    pag.press('space')
    # min is .04
    time.sleep(.04)


def earth(tile_map, active_piece, queue):
    tile_map.append(active_piece)
    first_selection = hands_engine(tile_map, current_level=1)
    temp_first = []
    for a in first_selection:
        a.append(queue[0])
        temp_first.append(a)
    first_selection = temp_first
    # print('selection format:', first_selection[0])
    # print(2, first_selection)

    # add potential multithreading support
    # with concurrent.futures.ProcessPoolExecutor() as runner:
    #     second_selection = runner.map(hands_engine, first_selection)
    #     hold = []
    #     print(second_selection)
    #     for a in second_selection:
    #         print('second', a)
    #         hold.append(a)
    for a in first_selection:
        print(2)
        second_selection.append(hands_engine(a[2], queue[0]))
    third_selection = []
    hold = []
    for a in second_selection:
        for b in a:
            print(3)
            hold.append(hands_engine(b[2], queue[1]))
        third_selection.append(hold)
    print('out', hold)
    best = ''
    lowest = 99
    for num_a, a in enumerate(hold):
        for b in a:
            height_array = get_heights(b[2])
            avg_height = height_array.sum() / len(height_array)
            print('tested')
            if avg_height < lowest:
                best = first_selection[num_a][1]
                lowest = avg_height

    print('placed', best, piece)
    # best = filter_options(first_selection, queue, 0)
    execute_offset(best)


if __name__ == '__main__':
    # True if using saved cords
    cord_map, queue_map = get_cord_wrapper(True)
    input('Ready!>')
    time.sleep(2)
    pag.press('f4')
    time.sleep(1.9)
    end = 0
    while True:  # get state, calculate best move, execute action
        field_map = get_field(cord_map)
        known_queue = get_queue(queue_map)
        print('queue:', known_queue)
        piece = field_map[0][4]
        if piece != 0:
            end = 0
            earth(field_map, piece, known_queue)
        else:
            end += 1
            time.sleep(.1)
        if end > 10:
            print('Game Over')
            breakpoint()
