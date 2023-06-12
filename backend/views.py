from flask import render_template, request
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
whitemode = 0
blackmode = 0
modenum = 0
exenum = 0
turncount = 0

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
    db = GameModel()
    db.__init__()

    if request.method == 'POST':
        global turn,candidate,turncount
        
        data = request.get_json()
        x = int(data['x'])
        y = int(data['y'])
        value = int(data['value'])
        
        db.save_move(turncount,turn,value,y*10+x)
        db.close()
        
        Reverse_func(x, y, value)
        create_candidate()
        turn = -turn
        turncount += 1

        data = create_json()
        
        return json.dumps(data)

    elif(request.method == 'GET'):
        if((blackmode if turn == black else whitemode) == 1):
            randmoves = []
            color = 0 if turn == black else 1
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    if(candidate[y][x][color] != 0):
                        randmoves.append([x, y])

            move = random.choice(randmoves)
            db.save_move(turncount,turn,1,move[1]*10+move[0])
            db.close()
            
            Reverse_func(move[0], move[1], abs(turn))
            create_candidate()
            turn = -turn
            turncount += 1

            data = create_json()
            return json.dumps(data)


def create_json():
    global turn
    global candidate
    data = {}
    data["gameboard"] = board.tolist()
    data["candidate"] = candidate.tolist()
    data["checkmate"] = False
    color = 0 if turn == black else 1
    if(sum([(candidate[x][y][color]) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)])):
        data["turn"] = turn
        data["skipped"] = False
    else:
        color = 0 if turn == white else 1
        if (checkmate_func()):
            data['checkmate'] = True
        turn = -turn
        data["turn"] = turn
        data['skipped'] = True
    return data


def checkmate_func():
    bpoint = wpoint = 0
    if(not(sum([(candidate[x][y][0]) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]))):
        if(not(sum([(candidate[x][y][1]) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]))):
            db = GameModel()
            db.__init__()
            for y in range(BOARD_SIZE):
                for x in range(BOARD_SIZE):
                    if(np.sign(board[y][x]) == black):
                        bpoint += board[y][x]
                    else:
                        wpoint += -board[y][x]
            winner = black if bpoint > wpoint else white
            db.save_game_result(winner,blackmode,whitemode,modenum)
            return True
    return False


def Reverse_func(x, y, value):
    global turn
    board[y][x] = value * turn
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
    global board, candidate, whitemode, blackmode, exenum, turn , turncount

    if request.method == 'POST':
        data = request.get_json()
        whitemode = data['white']
        blackmode = data['black']
        modenum = data['modenum']
        exenum = data['exenum']
        turn = black
        turncount = 1

        board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        candidate = np.zeros((BOARD_SIZE, BOARD_SIZE, 2), dtype=int)
        if modenum == 0:
            board[2][2] = board[3][3] = white
            board[3][2] = board[2][3] = black
            create_candidate()

        data["gameboard"] = board.tolist()
        data["candidate"] = candidate.tolist()
        data["turn"] = turn
        return json.dumps(data)
