
from flask import Flask
from views import index, move,init

app = Flask(__name__)

# ルーティングの設定
app.add_url_rule('/', 'index', index, methods=['GET'])
app.add_url_rule('/move', 'move', move, methods=['POST'])
app.add_url_rule('/init', 'init', init, methods=['POST'])

if __name__ == '__main__':
    app.run()