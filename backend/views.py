from flask import render_template, request
import numpy as np
import json
import logging
from backend.debugger import raise_locals

logging.basicConfig(filename='app.log', level=logging.DEBUG)

"""
定数宣言
"""
BOARD_SIZE = 6
board = []
candidate = []
black = 1
white = -1
empty = 0
turn = 0
whitemode = 0
blackmode = 0
modenum = 0
exenum = 0

# 方向(２進数)
LEFT = 2**0  # =1
LEFTDOWN = 2**1  # =2
DOWN = 2**2  # =4
RIGHTDOWN = 2**3  # =8
RIGHT = 2**4  # =16
RIGHTUP = 2**5  # =32
UP = 2**6  # =64
LEFTUP = 2**7  # =128

# 周囲8方向を調べる配列
direction = [
    [0, -1, LEFT],  # 左
    [1, -1, LEFTDOWN],  # 左下
    [1, 0, DOWN],  # 下
    [1, 1, RIGHTDOWN],  # 右下
    [0, 1, RIGHT],  # 右
    [-1, 1, RIGHTUP],  # 右上
    [-1, 0, UP],  # 上
    [-1, -1, LEFTUP],  # 左上
]


def index_func():
    # ホームページの表示
    return render_template('index.html')


def move_func():
    if request.method == 'POST':
        global turn
        global candidate
        data = request.get_json()
        x = int(data['x'])
        y = int(data['y'])
        value = int(data['value'])
        board[y][x] = value * turn
        for i in range(len(direction)):
            dx = x
            dy = y
            color = 0 if turn == black else 1
            if(candidate[dy][dx][color] & direction[i][2]):
                while(True):
                    dx += direction[i][1]
                    dy += direction[i][0]
                    logging.debug(str(dy)+","+str(dx))
                    if(np.sign(board[dy][dx]) == turn):
                        break
                    board[dy][dx] *= -1

        turn = -turn
        create_candidate()
        data = {}
        data["gameboard"] = board.tolist()
        data["candidate"] = candidate.tolist()
        data["turn"] = turn
        return json.dumps(data)


def create_candidate():
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            candidate[y][x][0] = 0
            candidate[y][x][1] = 0
            neighborhood_search(x, y, black)
            neighborhood_search(x, y, white)
    return 0


@raise_locals
def neighborhood_search(x, y, turncolor):
    if(board[y][x] != empty):
        return
    for i in range(len(direction)):
        j = 1
        dx = x
        dy = y
        for j in range(BOARD_SIZE):
            dx += direction[i][1]
            dy += direction[i][0]

            if((not(dy in range(0, BOARD_SIZE)))
               or (not(dx in range(0, BOARD_SIZE)))):
                break

            if (board[dy][dx] == empty):
                break

            if (np.sign(board[dy][dx]) == turncolor):
                if(j == 0):
                    break
                else:
                    color = 0 if turncolor == black else 1
                    candidate[y][x][color] = candidate[y][x][color] | direction[i][2]
                    break
    return 0


def init_func():
    global board, candidate, whitemode, blackmode, exenum, turn

    if request.method == 'POST':
        data = request.get_json()
        whitemode = data['white']
        blackmode = data['black']
        modenum = data['modenum']
        exenum = data['exenum']
        turn = black

        board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        candidate = np.zeros((BOARD_SIZE, BOARD_SIZE, 2), dtype=int)
        if modenum == 0:
            board[2][2] = board[3][3] = white
            board[3][2] = board[2][3] = black
            create_candidate()

        data = {}
        data["gameboard"] = board.tolist()
        data["candidate"] = candidate.tolist()
        data["turn"] = turn
        return json.dumps(data)
