from flask import render_template, request
import numpy as np
import json
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

"""
定数宣言
"""
BOARD_SIZE = 6
board = []
black = 1
white = -1
empty = 0

def index_func():
    # ホームページの表示
    return render_template('index.html')


def move_func():
    if request.method == 'POST':
        data = request.get_json()
        # ユーザーの入力（駒の移動など）の処理
        # データベースの更新やゲームの進行などを行う
        # 必要に応じて適切なレスポンスを返す
        return json.dumps(data)


def init_func():
    if request.method == 'POST':
        data = request.get_json()
        whitemode = data['white']
        blackmode = data['black']
        modenum = data['modenum']
        exenum = data['exenum']

        board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        if(modenum == 0):
            board[2][2] = board[3][3] = black
            board[3][2] = board[2][3] = white
        
        data = {}    
        data["gameboard"] = board.tolist()
        return json.dumps(data)
