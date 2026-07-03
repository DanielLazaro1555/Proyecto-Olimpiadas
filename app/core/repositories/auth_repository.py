import sqlite3


class AuthRepository:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def get_user_by_username(self, username):
        self.cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def create_user(self, username, password_hash, role):
        self.cursor.execute(
            "INSERT INTO usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        self.connection.commit()

    def list_users(self):
        self.cursor.execute("SELECT id, username, rol FROM usuarios ORDER BY id")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_user_by_id(self, user_id):
        self.cursor.execute("SELECT id FROM usuarios WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        self.connection.commit()

    def is_duplicate_username_error(self, error):
        return isinstance(error, sqlite3.IntegrityError)
