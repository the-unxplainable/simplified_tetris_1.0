"""
File: possible_tetris.py
----------------
This will be a very simplified version or basic stepping stone to tetris

TODO: Fix the down arrow clipping some blocks
TODO: Create scorelabel
TODO: Create intro
TODO: Ensure that moves are "legal" such as rotating next to a wall/block
"""

import tkinter
import random
import time
import math

CANVAS_WIDTH = 500      # Width of drawing canvas in pixels
CANVAS_HEIGHT = 1000    # Height of drawing canvas in pixels
UNIT_SIZE = 50          # Size of unit block within shape
Y_SPEED = 50
X_SPEED = 50


def main():
    canvas = make_canvas(CANVAS_WIDTH, CANVAS_HEIGHT, 'Simplified Tetris')
    draw_grid(canvas)

    block_locations, values = store_locations()
    while not is_game_over(values):  # Plays shapes until the game is over
        play_shape(canvas, block_locations)

    # How to center text?
    canvas.create_text(40, 500, anchor='w', font='Times 40', text='GAME OVER!')
    canvas.mainloop()


def is_game_over(values):
    return 0 in values


def rotate(points, angle, center):
    """
    This function returns new coordinates for the shape using trig functions
    This function was written with the help of stackoverflow
    """
    angle = math.radians(angle)  # Obtain angle in radians
    cos_val = math.cos(angle)  # Get the cosine value of the angle
    sin_val = math.sin(angle)  # Get the sine value of the angle
    cx, cy = center
    new_points = []
    for x_old, y_old in points:  # Iterate through points
        x_old -= cx
        y_old -= cy
        x_new = x_old * cos_val - y_old * sin_val
        y_new = x_old * sin_val + y_old * cos_val
        new_points.append([round(x_new + cx), round(y_new + cy)])
    return flatten(new_points)  # For some reason, requires flatten list


def pair_them_up(points):
    new_points = []
    for x in range(0, len(points), 2):
        for y in range(1, len(points), 2):
            if y == x + 1:
                new_points.append([points[x], points[y]])
    return new_points


def flatten(coords):
    flatten = []
    for coord in coords:
        for i in range(len(coord)):
            flatten.append(coord[i])
    return flatten


def draw_grid(canvas):
    for i in range(50, 500, 50):
        canvas.create_line(i, 0, i, 1000, fill='grey95')
    for i in range(50, 1000, 50):
        canvas.create_line(0, i, 500, i, fill='grey95')


# Plays one shape until shape is placed
def play_shape(canvas, block_locations):
    shape = make_randomized_shape(canvas)
    canvas.bind("<Key>", lambda event: key_pressed(event, canvas, shape))
    canvas.focus_set()  # Canvas now has the keyboard focus
    make_shape_fall(canvas, shape, block_locations)
    #place_shape(canvas, shape, block_locations)
    update_block_locations(canvas, shape, block_locations)
    return shape


def make_shape_fall(canvas, shape, block_locations):
    while not is_touching_bottom(canvas, shape) and not is_touching_top_of_block(canvas, shape, block_locations):
        canvas.move(shape, 0, Y_SPEED)
        canvas.update()
        time.sleep(1/10)


# Places the shape when it hits the bottom or top of a block
def place_shape(canvas, shape, block_locations):
    for location in left_x_locations():
        if location <= get_left_x(canvas, shape) <= location + UNIT_SIZE / 2:
            canvas.moveto(shape, location - 2 + UNIT_SIZE / 2, get_top_y(canvas, shape) - 2)
        # Why do I need the - 1 here and the - 2 for other polygons?


def is_touching_bottom(canvas, shape):
    return get_bottom_y(canvas, shape) > CANVAS_HEIGHT - Y_SPEED


def is_touching_top_of_block(canvas, shape, block_locations):
    left_x = int(get_left_x(canvas, shape)) + UNIT_SIZE // 2
    right_x = int(get_right_x(canvas, shape))
    step = UNIT_SIZE
    if left_x > right_x:
        step *= -1
    for x in range(left_x, right_x, UNIT_SIZE):
        if block_locations[x] == get_bottom_y_of_x(canvas, shape, x - UNIT_SIZE // 2):
            return True
    return False


# Get position functions
def get_all_x(canvas, shape):
    x_indexes = []
    for index in range(len(canvas.coords(shape))):
        if index % 2 == 0:
            x_indexes.append(canvas.coords(shape)[index])
    x_indexes.sort()
    return x_indexes


def get_all_y(canvas, shape):
    y_indexes = []
    for index in range(len(canvas.coords(shape))):
        if index % 2 != 0:
            y_indexes.append(canvas.coords(shape)[index])
    y_indexes.sort()
    return y_indexes


def get_top_y_of_x(canvas, shape, x):
    # For this function I want to get a top y for the x given of a shape
    coords = canvas.coords(shape)
    top_y = CANVAS_HEIGHT
    for i in range(0, len(coords) - 2, 2):
        if coords[i] <= x + UNIT_SIZE // 2 <= coords[i + 2] and coords[i + 1] < top_y:
            top_y = coords[i + 1]
    if coords[-2] <= x + UNIT_SIZE // 2 <= coords[0] and coords[1] < top_y:
        top_y = coords[1]
    return top_y


def get_bottom_y_of_x(canvas, shape, x):
    # For the given x of a shape, I want to get the bottom y
    coords = canvas.coords(shape)
    bottom_y = 0
    for i in range(0, len(coords) - 2, 2):
        if coords[i] >= x + UNIT_SIZE // 2 >= coords[i + 2]:
            if coords[i + 1] > bottom_y:
                bottom_y = coords[i + 1]
    return bottom_y


def get_left_x(canvas, shape):
    return get_all_x(canvas, shape)[0]


def get_top_y(canvas, shape):
    return get_all_y(canvas, shape)[0]


def get_right_x(canvas, shape):
    return get_all_x(canvas, shape)[-1]


def get_bottom_y(canvas, shape):
    return max(get_all_y(canvas, shape))


def get_middle_x(canvas, shape):
    return canvas.coords(shape)[0] + UNIT_SIZE


def get_center(points):
    small_x = CANVAS_WIDTH
    big_y = 0
    for x, y in points:
        if x < small_x:
            small_x = x
        if y > big_y:
            big_y = y
    center = (small_x + 50, big_y - 50)
    return center


# Locations that shapes have to move to once placed
def store_locations():
    """
    Stores the locations as a dictionary with top y as values
    Increments of 50 starting at 25 (the midpoing of a UNIT)
    This is how the block will know when to stop falling
    """
    block_locations = {}
    for position in left_x_locations():
        block_locations[position] = None
    values = block_locations.values()
    return block_locations, values


def update_block_locations(canvas, shape, block_locations):
    left_x = int(get_left_x(canvas, shape)) + UNIT_SIZE // 2
    right_x = int(get_right_x(canvas, shape))
    for x in range(left_x, right_x, UNIT_SIZE):
        block_locations[x] = get_top_y_of_x(canvas, shape, x - UNIT_SIZE // 2)


def top_y_locations():
    possible_top_y_locations = []
    for i in range(0, CANVAS_HEIGHT, UNIT_SIZE):
        possible_top_y_locations.append(i)
    return possible_top_y_locations


def left_x_locations():
    # Gets the middle of the left most unit
    possible_left_x_locations = []
    for i in range(25, CANVAS_WIDTH, UNIT_SIZE):
        possible_left_x_locations.append(i)
    return possible_left_x_locations


# Creates a shape
def make_randomized_shape(canvas):
    num = random.randint(1, 7)
    if num == 1:
        return make_z_shape(canvas)
    elif num == 2:
        return make_s_shape(canvas)
    elif num == 3:
        return make_t_shape(canvas)
    elif num == 4:
        return make_r_el_shape(canvas)
    elif num == 5:
        return make_el_shape(canvas)
    elif num == 6:
        return make_long_rect(canvas)
    elif num == 7:
        return make_square_shape(canvas)


def make_z_shape(canvas):  # 16 points
    shape_start = CANVAS_WIDTH / 2 - UNIT_SIZE
    points = [
        [shape_start, 0],
        [shape_start + 2 * UNIT_SIZE, 0],
        [shape_start + 2 * UNIT_SIZE, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 3, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 3, + UNIT_SIZE * 2],
        [shape_start + UNIT_SIZE, UNIT_SIZE * 2],
        [shape_start + UNIT_SIZE, UNIT_SIZE],
        [shape_start, UNIT_SIZE],
    ]

    return canvas.create_polygon(points, outline='black', fill='aqua')


def make_s_shape(canvas):  # 16 points
    shape_start = CANVAS_WIDTH / 2 - UNIT_SIZE
    points = [
        [shape_start, UNIT_SIZE],
        [shape_start + UNIT_SIZE, UNIT_SIZE],
        [shape_start + UNIT_SIZE, 0],
        [shape_start + UNIT_SIZE * 3, 0],
        [shape_start + UNIT_SIZE * 3, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 2, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 2, UNIT_SIZE * 2],
        [shape_start, UNIT_SIZE * 2],
    ]

    return canvas.create_polygon(points, outline='black', fill='yellow')


def make_t_shape(canvas):  # 16 points
    shape_start = CANVAS_WIDTH / 2 - UNIT_SIZE
    points = [
        [shape_start, UNIT_SIZE],
        [shape_start + UNIT_SIZE, UNIT_SIZE], 
        [shape_start + UNIT_SIZE, 0],
        [shape_start + UNIT_SIZE * 2, 0],
        [shape_start + UNIT_SIZE * 2, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 3, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 3, UNIT_SIZE * 2],
        [shape_start, UNIT_SIZE * 2],
    ]

    return canvas.create_polygon(points, outline='black', fill='orange')


def make_r_el_shape(canvas):  # 12 points
    shape_start = CANVAS_WIDTH / 2 - UNIT_SIZE
    points = [
        [shape_start, 0],
        [shape_start + UNIT_SIZE, 0],
        [shape_start + UNIT_SIZE, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 3, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 3, UNIT_SIZE * 2],
        [shape_start, UNIT_SIZE * 2],
    ]

    return canvas.create_polygon(points, outline='black', fill='blue')


def make_el_shape(canvas):  # 12 points
    shape_start = CANVAS_WIDTH / 2 - UNIT_SIZE
    points = [
        [shape_start, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 2, UNIT_SIZE],
        [shape_start + UNIT_SIZE * 2, 0],
        [shape_start + UNIT_SIZE * 3, 0],
        [shape_start + UNIT_SIZE * 3, UNIT_SIZE * 2],
        [shape_start, UNIT_SIZE * 2],
    ]

    return canvas.create_polygon(points, outline='black', fill='green')


def make_long_rect(canvas):  # 8 points
    shape_start = CANVAS_WIDTH / 2 - UNIT_SIZE * 2
    points = [
        [shape_start, 0],
        [shape_start + UNIT_SIZE * 4, 0],
        [shape_start + UNIT_SIZE * 4, UNIT_SIZE],
        [shape_start, UNIT_SIZE]
    ]

    return canvas.create_polygon(points, fill='red', outline='black')


def make_square_shape(canvas):  # 8 points
    shape_start = CANVAS_WIDTH / 2 - UNIT_SIZE
    points = [
        [shape_start, 0],
        [shape_start + UNIT_SIZE * 2, 0],
        [shape_start + UNIT_SIZE * 2, UNIT_SIZE * 2],
        [shape_start, UNIT_SIZE * 2],
    ]

    return canvas.create_polygon(points, fill='purple', outline='black')


# DO NOT MODIFY - Creates and returns a drawing canvas
def make_canvas(width, height, title):
    """
    Create a canvas with specified dimension
    """
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1)
    canvas.pack()
    return canvas


def key_pressed(event, canvas, shape):
    """
    Respond to different arrow keys
    This was written with the help of Code In Place Section Leader
    """
    sym = event.keysym.lower()
    if sym == "left" and get_left_x(canvas, shape) >= UNIT_SIZE:
        canvas.move(shape, -UNIT_SIZE, 0)
    elif sym == "right" and get_right_x(canvas, shape) <= CANVAS_WIDTH - UNIT_SIZE:
        canvas.move(shape, UNIT_SIZE, 0)
    elif sym == "up":
        points = pair_them_up(canvas.coords(shape))  
        center = get_center(points)
        new_points = rotate(points, 90, center)
        canvas.coords(shape, new_points)
    elif sym == "down":
        canvas.move(shape, 0, UNIT_SIZE)


if __name__ == '__main__':
    main()
