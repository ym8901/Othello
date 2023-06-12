import mysql.connector


class GameModel:
    def __init__(self):
        # データベース接続の設定
        self.db = mysql.connector.connect(
            host='localhost',
            user='ym2003',
            password='8901Reimu',
            database='myDB'
        )
        self.cursor = self.db.cursor()

        # gamesテーブルの作成
        self.create_games_table()

        # movesテーブルの作成
        self.create_moves_table()

    def create_games_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                winner VARCHAR(255),
                blackmode INT,
                whitemode INT,
                mode INT,
                date_played DATETIME
            )
        ''')
        self.db.commit()

    def create_moves_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS moves (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_id INT,
                turn INT,
                player VARCHAR(255),
                score INT,
                position VARCHAR(255),
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')
        self.db.commit()

    def save_game_result(self, winner, blackmode, whitemode, mode):
        query = 'INSERT INTO games (winner,blackmode,whitemode,mode,date_played) VALUES (%s,%s,%s,%s,NOW())'
        values = (winner, blackmode, whitemode, mode)
        self.cursor.execute(query, values)
        self.db.commit()
        game_id = self.cursor.lastrowid  # 最後に挿入された行のIDを取得
        return game_id

    def save_move(self, game_id, turn, player, score, position):
        query = 'INSERT INTO moves (game_id, turn, player, score, position) VALUES (%s, %s, %s, %s, %s)'
        values = (game_id, turn, player, score, position)
        self.cursor.execute(query, values)
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()
