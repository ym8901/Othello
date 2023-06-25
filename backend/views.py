from flask import render_template, request, Response, jsonify
from functools import wraps
import numpy as np
import json
import logging
from backend.debugger import raise_locals
from backend.models import GameModel
import random

logging.basicConfig(filename='app.log', level=logging.DEBUG, encoding='utf-8')

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
selectmode = [0, 0]
modenum = 0
turncount = 0

db = GameModel()

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

blackstone = [10, 4, 4]
whitestone = [10, 4, 4]


def index_func():
    # ホームページの表示
    return render_template('index.html')


def use_database(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db.__init__()
        result = func(*args, **kwargs)
        db.close()
        return result
    return wrapper


@use_database
def move_func():
    global turn, candidate, turncount
    if request.method == 'POST':

        data = request.get_json()
        x = int(data['x'])
        y = int(data['y'])
        value = int(data['value'])

        db.save_process(turncount, turn, value, y*10+x)
        if(modenum):
            if(turn == black):
                blackstone[0 if value == 100 else 1 if value == 50 else 2] -= 1
            else:
                whitestone[0 if value == 100 else 1 if value == 50 else 2] -= 1
        Reverse_func(x, y, value)
        create_candidate()
        turn = -turn
        turncount += 1

        data = create_json()

        return json.dumps(data)

    elif(request.method == 'GET'):
        if((selectmode[0] if turn == black else selectmode[1]) == 1):
            random_move()
            data = create_json()
            return json.dumps(data)


@use_database
def random_move():
    global turn, turncount

    randmoves = []
    color = 0 if turn == black else 1
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if(candidate[y][x][color] != 0):
                randmoves.append([y, x])

    move = random.choice(randmoves)
    value = 1
    randvalue = []
    if(modenum):

        if((blackstone[0] if turn == black else whitestone[0]) > 0):
            randvalue += [100]
        if((blackstone[1] if turn == black else whitestone[1]) > 0):
            randvalue += [50]
        if((blackstone[2] if turn == black else whitestone[2]) > 0):
            randvalue += [10]
        if(len(randvalue)):
            value = random.choice(randvalue)
        else:
            turn = -turn
            return

        if(turn == black):
            blackstone[0 if value == 100 else 1 if value == 50 else 2] -= 1
        else:
            whitestone[0 if value == 100 else 1 if value == 50 else 2] -= 1

    db.save_process(turncount, turn, value, move[0]*10+move[1])
    Reverse_func(move[1], move[0], value)
    create_candidate()
    turncount += 1
    turn = -turn
    return


def AI_move():
    turn *= -1


def create_json():
    global turn
    data = {}
    if(modenum != 0):
        data["bs"] = blackstone
        data["ws"] = whitestone
    data["gameboard"] = board.tolist()
    data["candidate"] = candidate.tolist()
    data["checkmate"] = 0
    color = 0 if turn == black else 1
    if(sum([(candidate[x][y][color]) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)])):
        if(not(modenum) or (np.sum(blackstone) if turn == black else np.sum(whitestone))):
            data["turn"] = turn
            data["skipped"] = False
    else:
        result = checkmate_func()
        if (result != 0):
            data["checkmate"] = result
        turn = -turn
        data["turn"] = turn
        data["skipped"] = True
    return data


@use_database
def checkmate_func():
    bpoint = wpoint = winner = 0
    # 現ターンのプレイヤーの置ける場所がなく、もう一方も置ける場所がないか石がない場合
    if(not(sum([(candidate[x][y][0 if turn == black else 1]) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]))) and ((not(sum([(candidate[x][y][0 if turn == white else 1]) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]))) or
                                                                                                                            ((turn == white and not(np.sum(blackstone))) or (turn == black and not(np.sum(whitestone))))):
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if(np.sign(board[y][x]) == black):
                    bpoint += board[y][x]
                else:
                    wpoint += -board[y][x]
        winner = black if bpoint > wpoint else white if bpoint < wpoint else 2
        db.save_game_result(winner, selectmode[0], selectmode[1], modenum)
        db.save_moves()

    return winner


def Reverse_func(x, y, value):
    global turn, turncount, modenum, board, candidate

    board[y][x] = value * turn
    if(modenum != 0 and turncount < 5):
        return
    for i in range(len(direction)):
        dx = x
        dy = y
        color = 0 if turn == black else 1
        if(candidate[dy][dx][color] & direction[i][2]):
            while(True):
                dx += direction[i][1]
                dy += direction[i][0]
                if(np.sign(board[dy][dx]) == turn):
                    break
                board[dy][dx] *= -1
    return


def create_candidate():
    global turn, turncount, modenum
    if(modenum != 0 and turncount < 4):
        candidate[2][3][0] = 1 if board[2][3] == empty else 0
        candidate[3][2][0] = 1 if board[3][2] == empty else 0
        candidate[2][2][1] = 1 if board[2][2] == empty else 0
        candidate[3][3][1] = 1 if board[3][3] == empty else 0
    else:
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


@use_database
def load_func():
    global turn, turncount, board, candidate, modenum, selectmode
    if request.method == 'GET':
        data = {}
        jdata = {}

        winner = db.get_gamewinner()

        if (int(winner) == 0):
            board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
            candidate = np.zeros((BOARD_SIZE, BOARD_SIZE, 2), dtype=int)
            data = db.load_processes()
            modenum = int(data["mode"])
            selectmode[0] = int(data["selectmode"][0])
            selectmode[1] = int(data["selectmode"][1])
            if(modenum == 0):
                board[2][2] = board[3][3] = white
                board[3][2] = board[2][3] = black

            else:
                blackstone[0] = whitestone[0] = 10
                blackstone[1] = whitestone[1] = 4
                blackstone[2] = whitestone[2] = 4

            create_candidate()
            for i in range(len(data["player"])):
                turn = int(np.sign(data["player"][i]))
                turncount = i+1
                if(modenum == 1):
                    if (turn == black):
                        blackstone[0 if abs(data["score"][i]) == 100 else 1 if abs(
                            data["score"][i]) == 50 else 2] -= 1
                    else:
                        whitestone[0 if abs(data["score"][i]) == 100 else 1 if abs(
                            data["score"][i]) == 50 else 2] -= 1

                Reverse_func(data["position"][i] %
                             10, data["position"][i]//10, data["score"][i])
                create_candidate()

            turn = -turn

            if(modenum != 0):
                jdata["bs"] = blackstone
                jdata["ws"] = whitestone
            jdata["selectmode"] = selectmode
            jdata["mode"] = modenum
            jdata["gameboard"] = board.tolist()
            jdata["candidate"] = candidate.tolist()
            jdata["turn"] = turn
            jdata["winner"] = 0

        else:
            jdata["winner"] = True
        return json.dumps(jdata)


def simulate_func():
    global selectmode, modenum, turn
    if request.method == 'POST':
        data = request.get_json()
        selectmode = data["selectmode"]
        modenum = data["modenum"]

    board_init()
    while(True):
        if((selectmode[0] if turn == black else selectmode[1]) == 1):
            random_move()
        data = create_json()
        if(data['checkmate']):
            break

    winner = data["checkmate"]

    return jsonify({'winner': winner})


@use_database
def board_init():
    global board, candidate, turn, modenum, turncount, blackstone, whitestone
    turn = black
    turncount = 1
    blackstone[0] = whitestone[0] = 10
    blackstone[1] = whitestone[1] = blackstone[2] = whitestone[2] = 4
    db.save_dummygame(selectmode[0], selectmode[1], modenum)

    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    candidate = np.zeros((BOARD_SIZE, BOARD_SIZE, 2), dtype=int)
    if modenum == 0:
        board[2][2] = board[3][3] = white
        board[3][2] = board[2][3] = black

    create_candidate()


def init_func():
    global board, candidate, selectmode, turn, modenum, turncount, blackstone, whitestone

    if request.method == 'POST':
        data = request.get_json()
        selectmode[1] = data['white']
        selectmode[0] = data['black']
        modenum = data['modenum']

        board_init()

        data["bs"] = blackstone
        data["ws"] = whitestone
        data["gameboard"] = board.tolist()
        data["candidate"] = candidate.tolist()
        data["turn"] = turn

        return json.dumps(data)
