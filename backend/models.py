import mysql.connector
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, encoding='utf-8')


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

        # processesテーブルの作成
        self.create_processes_table()

    def create_games_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                winner VARCHAR(255),
                blackmode INT,
                whitemode INT,
                mode INT
                
            )
        ''')
        self.db.commit()

    def create_moves_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS moves (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_id INT,
                turn INT,
                player INT,
                score INT,
                position INT,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
        ''')
        self.db.commit()

    def create_processes_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_id INT,
                turn INT,
                player INT,
                score INT,
                position INT
            )
        ''')
        self.db.commit()

    def save_game_result(self, winner, blackmode, whitemode, mode):
        query = 'UPDATE games SET winner = %s,blackmode = %s,whitemode = %s,mode = %s WHERE id = %s'
        values = (winner, blackmode, whitemode, mode, self.get_gameid())
        self.cursor.execute(query, values)

        dummy_query = 'INSERT INTO games (winner, blackmode, whitemode, mode) VALUES (NULL, NULL, NULL, NULL)'
        self.cursor.execute(dummy_query)
        self.db.commit()
        self.dummy_game_id = self.cursor.lastrowid

    def save_moves(self):
        query = 'INSERT INTO moves SELECT * FROM processes'
        self.cursor.execute(query)

        query = 'TRUNCATE table processes'
        self.cursor.execute(query)
        self.db.commit()

    def save_process(self, turn, player, score, position):
        if(self.get_gameid() == None):
            # ダミーレコードの挿入
            dummy_query = 'INSERT INTO games (winner, blackmode, whitemode, mode) VALUES (NULL, NULL, NULL, NULL)'
            self.cursor.execute(dummy_query)
            self.db.commit()
            dummy_game_id = self.cursor.lastrowid  # ダミーレコードのgame_idを取得

            # Processesテーブルに行を追加
            query = 'INSERT INTO Processes (game_id, turn, player, score, position) VALUES (%s, %s, %s, %s, %s)'
            values = (dummy_game_id, turn, player, score, position)
            self.cursor.execute(query, values)
            self.db.commit()
        else:
            # Processesテーブルに行を追加
            query = 'INSERT INTO Processes (game_id, turn, player, score, position) VALUES (%s, %s, %s, %s, %s)'
            values = (self.get_gameid(), turn, player, score, position)
            self.cursor.execute(query, values)
            self.db.commit()

    def get_gameid(self):
        query = 'SELECT MAX(id) FROM games'
        self.cursor.execute(query)
        game_id = self.cursor.fetchone()[0]
        return game_id

    def load_processes(self):
        query = 'SELECT * FROM processes'
        self.cursor.execute(query)

        processes = []
        for fetched_line in self.cursor.fetchall():
            processes.append(
                [fetched_line["player"], fetched_line["score"], fetched_line["position"]])

        return processes

    def close(self):
        self.cursor.close()
        self.db.close()
