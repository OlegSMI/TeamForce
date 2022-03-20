import sqlite3
from loguru import logger

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id:int):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return bool(len(result.fetchall()))

    def add_user(self, user_id:int, user_name:str):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO users (user_id, user_name) VALUES (?, ?)", (user_id, user_name))
        return self.conn.commit()

    def topic_exists(self, user_id:int):
        """Проверяем все темы пользователя"""
        mas = []
        result = self.cursor.execute("SELECT topic FROM data WHERE user_id=(SELECT id FROM users WHERE user_id = ?)", (user_id,))
        for res in result.fetchall():
            mas.append(res['topic'])
        return mas

    def add_topic(self, topic:str, user_id:int):
        """Добавляем тему в базу"""
        self.cursor.execute("INSERT INTO data(topic, user_id) SELECT ?, id FROM users WHERE user_id = ? LIMIT 1", (topic, user_id))
        return self.conn.commit()

    def filter_topic(self):
        mas = []
        result = self.cursor.execute("SELECT topic from data")
        for res in result:
            mas.append(res['topic'])
        return mas

    def add_chois_user(self, user_id:int):
        self.cursor.execute("INSERT INTO choices_users (user_id) VALUES (?)", (user_id, ))
        return self.conn.commit()

    def add_banned_user(self, user_id:int):
        self.cursor.execute("INSERT INTO banned_users (user_id) VALUES (?)", (user_id,))
        return self.conn.commit()

    def select_all_choices_users(self):
        mas = []
        result = self.cursor.execute("SELECT * FROM choices_users")
        for res in result:
            if res['user_id'] not in mas:
                mas.append(res['user_id'])
        logger.debug(mas)
        return mas

    def select_all_banned_users(self):
        mas = []
        result = self.cursor.execute("SELECT * FROM banned_users")
        for res in result:
            mas.append(res['user_id'])
        return mas

    def clean_table_choices_users(self):
        self.cursor.execute("DELETE from choices_users")
        return self.conn.commit()

    def get_users_from_topic(self, topic:str):
        mas = {}
        result = self.cursor.execute("SELECT users.user_name, users.user_id FROM users WHERE data.topic = ?", (topic,))
        for res in result:
            mas[res['user_name']] = [res['user_id']]
        return mas

    def get_all_data(self):
        mas = {}
        result = self.cursor.execute("SELECT users.user_name, users.user_id FROM users")
        for res in result:
            mas[res['user_name']] = [res['user_id']]
        return mas

    def all_emails(self):
        mas = []
        result = self.cursor.execute("SELECT email FROM emails")
        for res in result:
            mas.append(res['email'])
        return mas

    def add_email(self, email:str):
        self.cursor.execute("INSERT INTO emails (email) VALUES (?)", (email,))
        return self.conn.commit()
