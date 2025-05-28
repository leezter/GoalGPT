import sqlite3
from data_manager_interface import AbstractDataManager


class SQLiteDataManager(AbstractDataManager):
    def __init__(self, db_path=database.db):
        """
        Initialize the SQLiteDataManager with a connection to the specified SQLite database.
        Args:
            db_path (str): Path to the SQLite database file. Defaults to 'database.db'.
        """
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row


    def get_user(self, user_id):
        """
        Retrieve a user from the database by user ID.
        Args:
            user_id (int): The ID of the user to retrieve.
        Returns:
            sqlite3.Row: The user record, or None if not found.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()


    def save_goal(self, user_id, goal):
        """
        Save a new goal for a user in the database.
        Args:
            user_id (int): The ID of the user.
            goal (dict): A dictionary containing goal details, must include 'description'.
        """
        cur = self.conn.cursor()
        cur.execute("INSERT INTO goals (user_id, description) VALUES (?, ?)", (user_id, goal['description']))
        self.conn.commit()


    def get_tasks_for_date(self, user_id, target_date):
        """
        Retrieve all tasks for a user on a specific date.
        Args:
            user_id (int): The ID of the user.
            target_date (str): The date for which to retrieve tasks (format: 'YYYY-MM-DD').
        Returns:
            list[sqlite3.Row]: List of task records for the given date.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE user_id = ? AND date = ?", (user_id, target_date))
        return cur.fetchall()
    

    # More methods like save_task, mark_task_done, etc. will be added