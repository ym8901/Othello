from flask import Flask
from backend.views import index_func, move_func, init_func, load_func,simulate_func

app = Flask(__name__)
# ルーティングの設定

@app.route("/", methods=['GET'])
def index():
    return index_func()

@app.route('/move', methods=['POST', 'GET'])
def move():
    return move_func()

@app.route('/init',  methods=['POST'])
def init():
    return init_func()

@app.route('/load', methods=['GET'])
def load():
    return load_func()

@app.route('/simulate', methods=['POST'])
def simulate():
    return simulate_func()

if __name__ == '__main__':
    app.run(debug=True)