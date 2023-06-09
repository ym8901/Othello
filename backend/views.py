from flask import render_template, request
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

def index_func():
    # ホームページの表示
    return render_template('index.html')


def move_func():
    if request.method == 'POST':
        # ユーザーの入力（駒の移動など）の処理
        # データベースの更新やゲームの進行などを行う
        # 必要に応じて適切なレスポンスを返す
        return 'Move successful'


def init_func():
    if request.method == 'POST':
        data = request.get_json()
        logging.debug(data) 
        white = data['white']
        black = data['black']
        modenum = data['modenum']
        exenum = data['exenum']
        
    return 0
