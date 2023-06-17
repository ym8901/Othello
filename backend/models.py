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
        self.db.commit()

    def save_moves(self):
        query = 'INSERT INTO moves (game_id, turn, player, score, position) SELECT game_id, turn, player, score, position FROM processes'
        self.cursor.execute(query)

        query = 'TRUNCATE table processes'
        self.cursor.execute(query)
        self.db.commit()

    def save_process(self, turn, player, score, position):
        # Processesテーブルに行を追加
        query = 'INSERT INTO Processes (game_id, turn, player, score, position) VALUES (%s, %s, %s, %s, %s)'
        values = (self.get_gameid(), turn, player, score, position)
        self.cursor.execute(query, values)
        self.db.commit()

    def save_dummygame(self, blackmode, whitemode, mode):
        query = 'INSERT INTO games (winner, blackmode, whitemode, mode) VALUES (0, %s, %s, %s)'
        values = (blackmode, whitemode, mode)
        self.cursor.execute(query, values)
        self.db.commit()

    def get_gameid(self):
        query = 'SELECT MAX(id) FROM games'
        self.cursor.execute(query)
        game_id = self.cursor.fetchone()[0]
        result = self.cursor.fetchone()
        if result is not None:
            game_winner = result[0]
        else:
            game_winner = None
        self.db.commit()
        return game_id

    def get_gamewinner(self):
        query = 'SELECT winner FROM games WHERE id = %s'
        values = (self.get_gameid(),)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result is not None:
            game_winner = result[0]
        else:
            game_winner = True
        self.db.commit()
        return game_winner

    def load_processes(self):
        query = 'SELECT * FROM processes'
        self.cursor.execute(query)

        player = []
        score = []
        position = []
        processes = {}
        for fetched_line in self.cursor.fetchall():
            player.append(fetched_line[3])
            score.append(fetched_line[4])
            position.append(fetched_line[5])

        query = 'SELECT * FROM games WHERE id = %s'
        values = (self.get_gameid(),)
        self.cursor.execute(query, values)

        for games in self.cursor.fetchall():
            processes["blackmode"] = games[2]
            processes["whitemode"] = games[3]
            processes["mode"] = games[4]

        processes["player"] = player
        processes["score"] = score
        processes["position"] = position

        self.db.commit()
        return processes

    def close(self):
        self.cursor.close()
        self.db.close()
