import board
import random
import time
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import KeysScanner
from kmk.keys import KC
from kmk.extensions.neopixel import NeoPixel

keyboard = KMKKeyboard()
keyboard.matrix = KeysScanner([board.D0, board.D1, board.D2, board.D3])

NUM_PIXELS = 16
PIXEL_PIN = board.GP14

np = NeoPixel(pixel_pin=PIXEL_PIN, num_pixels=NUM_PIXELS, auto_write=True)
keyboard.extensions.append(np)

colors = [
    (0, 0, 0),         # 0 - Empty
    (40, 0, 0),        # 1
    (80, 0, 0),        # 2
    (120, 30, 0),      # 3
    (160, 60, 0),      # 4
    (200, 100, 0),     # 5
    (230, 150, 0),     # 6
    (255, 180, 30),    # 7
    (255, 210, 70),    # 8
    (255, 230, 110),   # 9
    (200, 255, 80),    # 10
    (120, 255, 120),   # 11
    (60, 180, 255),    # 12
    (30, 120, 255),    # 13
    (120, 60, 255),    # 14
    (255, 255, 255),   # 15 - Final color
]

grid = [[0 for _ in range(4)] for _ in range(4)]

def dispTiles():
    for y in range(4):
        for x in range(4):
            idx = y * 4 + x
            np.pixels[idx] = colors[grid[y][x]]

def spawn():
    empty = [(y, x) for y in range(4) for x in range(4) if grid[y][x] == 0]
    if empty:
        y, x = random.choice(empty)
        grid[y][x] = 1

def merge(line):
    new_line = [i for i in line if i != 0]
    i = 0
    while i < len(new_line) - 1:
        if new_line[i] == new_line[i + 1] and new_line[i] < len(colors) - 1:
            new_line[i] += 1
            new_line[i + 1] = 0
            i += 2
        else:
            i += 1
    new_line = [i for i in new_line if i != 0]
    return new_line + [0] * (4 - len(new_line))

def left():
    changed = False
    for y in range(4):
        old = grid[y][:]
        new = merge(old)
        grid[y] = new
        if old != new:
            changed = True
    return changed

def right():
    changed = False
    for y in range(4):
        old = grid[y][:]
        new = merge(old[::-1])[::-1]
        grid[y] = new
        if old != grid[y]:
            changed = True
    return changed

def up():
    changed = False
    for x in range(4):
        col = [grid[y][x] for y in range(4)]
        new = merge(col)
        for y in range(4):
            if grid[y][x] != new[y]:
                grid[y][x] = new[y]
                changed = True
    return changed

def down():
    changed = False
    for x in range(4):
        col = [grid[y][x] for y in range(4)]
        new = merge(col[::-1])[::-1]
        for y in range(4):
            if grid[y][x] != new[y]:
                grid[y][x] = new[y]
                changed = True
    return changed

def playable():
    for y in range(4):
        for x in range(4):
            val = grid[y][x]
            if val == 0:
                return True
            if x < 3 and grid[y][x] == grid[y][x + 1]:
                return True
            if y < 3 and grid[y][x] == grid[y + 1][x]:
                return True
    return False

def won():
    for row in grid:
        if 15 in row:
            return True
    return False

def fade(delay=0.05):
    for step in range(10, -1, -1):
        for idx in range(NUM_PIXELS):
            r, g, b = np.pixels[idx]
            r = int(r * step / 10)
            g = int(g * step / 10)
            b = int(b * step / 10)
            np.pixels[idx] = (r, g, b)
        time.sleep(delay)

def restart():
    global grid
    grid = [[0 for _ in range(4)] for _ in range(4)]
    spawn()
    spawn()
    dispTiles


keyboard.keymap = [[KC.A, KC.B, KC.C, KC.D]]  # A=Up, B=Down, C=Left, D=Right

key_action = {
    KC.A: up,
    KC.B: down,
    KC.C: left,
    KC.D: right,
}

def loop():
    restart()
    while True:
        keyboard.update()
        for row in keyboard.keymap:
            for key in row:
                if keyboard[key].pressed:
                    moved = key_action[key]()
                    if moved:
                        spawn()
                        dispTiles()
                        time.sleep(0.2)
                    if won() or not playable():
                        time.sleep(0.5)
                        fade()
                        time.sleep(0.5)
                        restart()
        time.sleep(0.05)

if __name__ == '__main__':
    loop()