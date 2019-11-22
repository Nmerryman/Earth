import tkinter as tk
import time
import win32gui
import win32ui
import pyautogui as pag

it = 1


# take corners from top left in clockwise pattern, only need 3
def get_corners():
    def append_cords(data):
        corners.append((data.x, data.y))
        if len(corners) == 3:
            time.sleep(.2)
            root.destroy()
        print(data.x, data.y)

    def key(given_key):
        # stop program when press esc
        if given_key.keycode == 27:
            root.destroy()
        print(given_key)

    corners = []
    root = tk.Tk()
    root.title('test')
    root.attributes('-alpha', .5)
    s_width = root.winfo_screenwidth()
    s_height = root.winfo_screenheight()
    print(s_width, s_height)
    root.geometry('700x500')
    root.overrideredirect(True)
    root.geometry(f'{s_width}x{s_height}+0+0')
    root.bind('<Key>', key)
    root.bind('<Button 1>', append_cords)
    root.mainloop()
    print(corners[0][0])
    delta_x = (corners[1][0] - corners[0][0]) / 9
    delta_y = (corners[2][1] - corners[0][1]) / 19
    print(delta_x, delta_y)
    real_cords = []
    for a in range(20):
        hold = []
        for b in range(20):
            hold.append((int(corners[0][0] + b * delta_x), int(corners[0][1] + a * delta_y)))
        real_cords.append(hold)
    return real_cords


def get_field_cords():
    def append_cords(data):
        corners.append((data.x, data.y))
        if len(corners) == 3:
            time.sleep(.2)
            root.destroy()
        print(data.x, data.y)

    def key(given_key):
        # stop program when press esc
        if given_key.keycode == 27:
            root.destroy()
        print(given_key)

    corners = []
    root = tk.Tk()
    root.title('test')
    root.attributes('-alpha', .5)
    s_width = root.winfo_screenwidth()
    s_height = root.winfo_screenheight()
    print(s_width, s_height)
    root.geometry('700x500')
    root.overrideredirect(True)
    root.geometry(f'{s_width}x{s_height}+0+0')
    root.bind('<Key>', key)
    root.bind('<Button 1>', append_cords)
    root.mainloop()
    print(corners[0][0])
    delta_x = (corners[1][0] - corners[0][0]) / 9
    delta_y = (corners[2][1] - corners[0][1]) / 19
    print(delta_x, delta_y)
    real_cords = []
    for a in range(20):
        hold = []
        for b in range(10):
            hold.append((int(corners[0][0] + b * delta_x), int(corners[0][1] + a * delta_y)))
        real_cords.append(hold)
    return real_cords


# legacy
def hex_to_rgb(val):
    print(val)
    val = str(val)
    missing = 8 - len(val)
    val = val[:2] + (missing * '0') + val[2:]
    hex1 = int(val[2:4], 16)
    hex2 = int(val[4:6], 16)
    hex3 = int(val[6:8], 16)
    return hex3, hex2, hex1


def fix_hex(hex_val_in):
    if hex_val_in == '0x0':
        return '#000000'
    val = str(hex_val_in)
    missing = 8 - len(val)
    add = '' + '0' * missing
    # if missing == 4:
    #     add = '0000'
    # elif missing == 2:
    #     add = '00'
    val = add + val[2:]
    val = '#' + val[4:6] + val[2:4] + val[0:2]
    # print(val1, val)
    return val


def color_to_name(color):
    # print(type(color))
    black = ['#080808', '#020202', '#000000', '#2a2a2a']
    if isinstance(color, list):
        hold = []
        for a in color:
            hold.append(color_to_name(a))
        return hold
    elif black.__contains__(color):
        return ' '
    names = {'#d70f37': 'Z', '#b41851': 'Z', '#7c287e': 'Z', '#1a0106': 'Z', '#af298a': 'T', '#992378': 'T', '#2141c6': 'J', '#e35b02': 'L',
             '#59b101': 'S', '#4d9a00': 'S', '#0f9bd7': 'I', '#e39f02': 'O'}
    # print(color)
    try:
        give = names[color]
    except KeyError:
        give = color
    return give


def get_cord_colors(cypher):
    name = 'Jstris - Mozilla Firefox (Private Browsing)'
    name1 = 'Jstris - Mozilla Firefox'
    name2 = 'Hexadecimal Colour Codes | 101 Computing - Mozilla Firefox'
    w = win32ui.FindWindow(None, name1)
    # print(w)
    color_map = []
    # select lines here
    for a in cord_map:
        hold = []
        # get each in the line
        for data in a:
            dc = w.GetWindowDC()
            val = dc.GetPixel(data[0] + 1, data[1])
            hold.append(fix_hex(hex(val)))
            dc.DeleteDC()
        color_map.append(hold)
    return color_map


def get_cord_colors_field(cord_map):
    # this is for getting only the field
    name = 'Jstris - Mozilla Firefox (Private Browsing)'
    # use name1 for account/consistent controls
    name1 = 'Jstris - Mozilla Firefox'
    name2 = 'Hexadecimal Colour Codes | 101 Computing - Mozilla Firefox'
    w = win32ui.FindWindow(None, name)
    # print(w)
    color_map = []
    # select lines here
    for a in cord_map:
        hold = []
        # get each in the line
        for place, data in enumerate(a):
            dc = w.GetWindowDC()
            val = dc.GetPixel(data[0] + 1, data[1])
            hold.append(fix_hex(hex(val)))
            dc.DeleteDC()
        color_map.append(hold)
    return color_map


def show_only_field(cord_map):

    def update():
        colors = get_cord_colors_field(cord_map)
        for a in range(20):
            for b, interest in enumerate(boxes[a]):
                can.itemconfig(interest, fill=colors[a][b])
        root.after(200, update)

    def key(arg):
        print(arg)
        if arg.keysym == 'p':
            update()

    scale = 40
    root = tk.Tk()
    root.geometry('800x800')
    can = tk.Canvas(root)
    can.pack()
    can.config(width=800, height=800)
    boxes = []

    for y in range(20):
        hold = []
        for x in range(10):
            hold.append(can.create_rectangle(x * scale, y * scale, x * scale + scale, y * scale + scale, outline='#9f9f9f'))
        boxes.append(hold)
    root.bind('<Key>', key)
    update()
    root.mainloop()


def show_field(cord_map):

    def update():
        colors = get_cord_colors(cord_map)
        for a in range(20):
            for b, interest in enumerate(boxes[a]):
                can.itemconfig(interest, fill=colors[a][b])
        can.create_line(5 * scale, 0, 5 * scale, 20 * scale, width=3, fill='#ffffff')
        can.create_line(15 * scale, 0, 15 * scale, 20 * scale, width=3, fill='#ffffff')
        root.after(200, update)

    def key(arg):
        print(arg)
        if arg.keysym == 'p':
            update()

    scale = 40
    root = tk.Tk()
    root.geometry('800x800')
    can = tk.Canvas(root)
    can.pack()
    can.config(width=800, height=800)
    boxes = []

    for y in range(20):
        hold = []
        for x in range(20):
            hold.append(can.create_rectangle(x * scale, y * scale, x * scale + scale, y * scale + scale, outline='#9f9f9f'))
        boxes.append(hold)
    root.bind('<Key>', key)
    update()
    root.mainloop()


def column_heights(tile_map):
    # cord_map -> color_map -> tile_map
    heights = []
    for a in range(10):
        stop = 19
        caught = False
        for b in range(4, 19):
            if tile_map[b + 1][a] != ' ' and not caught:
                stop = b
                caught = True
        heights.append(str(19 - stop))
    return heights


def column_holes(tile_map, heights):
    holes = []
    for a, val in enumerate(heights):
        count = 0
        for b in range(int(val)):
            if tile_map[19 - b][a + 5] == ' ':
                count += 1
        holes.append(str(count))
        # print(holes)
    return holes


def check_active(tile_map):
    # redundant, but makes it more intuitive
    return tile_map[0][4]


# has some legacy stuff but should still work
def show_stats(cord_map):
    def capture():
        colors = get_cord_colors(cord_map)
        for a in colors:
            print(color_to_name(a))
        # check for new active piece
        if colors[0][10] != '#000000':
            active = color_to_name(colors[0][10])
            lab_active.config(text=active)
        heights = []
        # check for heights of each column
        for a in range(5, 15):
            count = 4
            while color_to_name(colors[count][a]) == ' ' and count < 19:
                count += 1
            heights.append(str(19 - count))
        lab_heights.config(text=heights)
        # check for holes in each column
        holes = []
        for a, val in enumerate(heights):
            count = 0
            for b in range(int(val)):
                if color_to_name(colors[19 - b][a + 5]) == ' ':
                    count += 1
            holes.append(str(count))
            # print(holes)
        lab_holes.config(text=holes)
        root.after(200000, capture)

    # def update():
    heights, active, holes, active_squares = [], '', [], []
    root = tk.Tk()
    root.geometry('200x200')
    tk.Label(root, text='Active Piece').pack()
    lab_active = tk.Label(root, text=active)
    lab_active.pack()
    tk.Label(root, text='Heights').pack()
    lab_heights = tk.Label(root, text=heights)
    lab_heights.pack()
    tk.Label(root, text='Holes').pack()
    lab_holes = tk.Label(root, text=holes)
    lab_holes.pack()
    capture()
    root.mainloop()


# legacy
def web_find(color_map, active):
    in_view = 0
    for a in color_map[:4]:
        for b in a:
            if b == active:
                in_view += 1
    if in_view != 4:
        return f'missing: {4 - in_view}'


# legacy
def rotate_active(color_map, active):
    if active == 'Z':
        for a in range(5):
            pass


def hard_drop(active_piece, offset, heights):
    # format will be rotations, direction of moves, moves -> '1+3'
    store = []
    center = eval('4' + offset[1:])
    # had to place str(int()) when ever there was height compensation
    if active_piece == 'Z':
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
    elif active_piece == 'S':
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
    elif active_piece == 'O':
        # no rotations possible
        # range: -4, 4
        store.append(int(heights[center]))
        store.append(int(heights[center + 1]))
    elif active_piece == 'I':
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
    elif active_piece == 'L':
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
    elif active_piece == 'J':
        # offset is weird because of copy and paste
        if offset[0] == '0':
            # range: -3, 4
            store.append(int(heights[center - 1]))
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]))
        elif offset[0] == '3':
            # range: -4, 4
            store.append(int(heights[center]))
            store.append(int(heights[center - 1]))
        elif offset[0] == '2':
            # range: -3, 4
            store.append(int(heights[center - 1]) - 1)
            store.append(int(heights[center]) - 1)
            store.append(int(heights[center + 1]))
        elif offset[0] == '1':
            # range: -4, 4
            store.append(int(heights[center]))
            store.append(int(heights[center + 1]) - 2)
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
    # print(store, cost, offset, heights)
    # new_heights = new_height_map(active_piece, offset, heights)
    return cost, min(store)


def new_height_map(current_height_map, active_piece, offset):
    piece_sizes = {''}


def clear(tile_map):
    for level, a in tile_map:
        cleared = True
        # turn false if there is no line clear condition
        for b in a[5: 15]:
            if b == ' ':
                cleared = False
        if cleared:
            # select up to clear, get cord and value of above line, and replace
            for b in range(level):
                for locate, c in enumerate(tile_map[level - b - 1]):
                    tile_map[level - b][locate] = c
    return tile_map


def execute_offset(offset, wait):
    time.sleep(wait)
    # rotations
    pag.press('up', presses=int(offset[0]))
    if offset[1] == '+':
        pag.press('right', presses=int(offset[2]))
    else:
        pag.press('left', presses=int(offset[2]))
    pag.press('space')


def ghost_engine(active_piece, height, delay=0):
    global it
    # todo removed tile_map and holes
    possibilities = {'Z': [(-3, 5), (-4, 5)], 'S': [(-3, 5), (-4, 5)], 'O': [(-4, 5)],
                     'I': [(-3, 3), (-5, 5)], 'L': [(-3, 5), (-4, 5), (-3, 5), (-3, 5)],
                     'J': [(-3, 5), (-4, 5), (-3, 5), (-4, 5)], 'T': [(-3, 5), (-4, 5), (-3, 5), (-3, 5)]}
    # set bad staring values
    score = 999999
    plan = ''
    options = []
    # cycle through rotations
    for a, b in enumerate(possibilities[active_piece]):
        for c in range(b[0], b[1]):
            # cycle through the possible offsets
            offset = f'{a}{c}'
            # add the + to the pos ones
            if len(offset) == 2:
                offset = offset[0] + '+' + offset[1]
            # get cost and compare to other costs from this offset
            cost, low = hard_drop(active_piece, offset, height)
            # print(cost)
            # restart list with best possible costs
            height_limit = 20
            # todo filter in a more robust system
            if cost < score and low < height_limit:
                options, score = [], cost
                options.append((cost, offset, low))
            # allow for multiple possible offsets
            elif cost == score and low < height_limit:
                options.append((cost, offset, low))
    best, lowest = '', 20
    print(options)
    for a in options:
        if a[2] < lowest:
            lowest = a[2]
            best = a[1]
    execute_offset(best, delay)


if __name__ == '__main__':
    # only set to true if field location has changed
    use_past_cords = True
    if use_past_cords:
        file = open('cords.txt', 'r')
        hold = file.read()
        cords = eval(hold)
    else:
        cords = get_field_cords()
        file = open('cords.txt', 'w')
        file.write(str(cords))
        file.close()
    # print(cords)
    # colors = get_cord_colors(cords)
    # for a in colors:
    #     print(a)
    # show_field(cords)
    # for a in cords:
    #     for b in a:
    #         pyautogui.moveTo(b[0], b[1])
    #         time.sleep(.1)
    # while True:
    #     exec(input('> '))
    # for a in cords:
    #     for b in a:
    #         pag.moveTo(b)
    #         input()
    input('Ready!>')
    time.sleep(3)
    pag.press('f4')
    time.sleep(1.9)
    print('check')
    while True:
        current_color_map = get_cord_colors_field(cords)
        current_tile_map = color_to_name(current_color_map)
        active_tile = check_active(current_tile_map)
        board_heights = column_heights(current_tile_map)
        # for a in current_tile_map:
        #     print(a)
        # time.sleep(2)
        ghost_engine(active_tile, board_heights)
    # show_stats(cords)
