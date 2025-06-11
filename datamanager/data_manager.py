import sqlite3
from .data_manager_interface import AbstractDataManager


class SQLiteDataManager(AbstractDataManager):
    def __init__(self, db_path="database.db"):
        """
        Initialize the SQLiteDataManager with a connection to the specified SQLite database.
        Args:
            db_path (str): Path to the SQLite database file. Defaults to 'database.db'.
        """
        self.db_path = db_path


    def get_connection(self):
        return sqlite3.connect(self.db_path)


    def get_user(self, user_id):
        """
        Retrieve a user from the database by user ID.
        Args:
            user _id (int): The ID of the user to retrieve.
        Returns:
            sqlite3.Row: The user record, or None if not found.
        """
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cur.fetchone()
        conn.close()
        return result


    def save_user(self, name, email, password_hash):
        """
        Save a new user to the database.
        Args:
            name (str): The name of the user.
            email (str): The email address of the user.
            password_hash (str): The hashed password of the user.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                    (name, email, password_hash))
        conn.commit()
        conn.close()


    def get_goals(self, user_id):
        """
        Retrieve all goals for a user from the database.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list[sqlite3.Row]: List of goal records for the user.
        """
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
        result = cur.fetchall()
        conn.close()
        return result


    def save_goal(self, user_id, goal):
        """
        Save a new goal for a user in the database.
        Args:
            user_id (int): The ID of the user.
            goal (dict): A dictionary containing goal details, must include 'description'.
        """
        description = goal['description']
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO goals (user_id, description) VALUES (?, ?)", (user_id, description))
        conn.commit()
        conn.close()


    def update_goal(self, goal_id, new_description):
        """
        Update the description of an existing goal in the database.
        Args:	
            goal_id (int): The ID of the goal to update.
            new_description (str): The new description for the goal.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE goals SET description = ? WHERE id = ?", (new_description, goal_id))
        conn.commit()
        conn.close()


    def delete_goal(self, goal_id):
        """
        Delete a goal from the database by its ID.
        Args:
            goal_id (int): The ID of the goal to delete.
        Returns:
            bool: True if a goal was deleted, False otherwise.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
        deleted = cur.rowcount > 0
        conn.close()
        return deleted


    def get_weekly_plan(self, goal_id, week_start_date):
        """
        Retrieve the weekly plan for a specific goal starting from a given date.
        Args:
            goal_id (int): The ID of the goal.
            week_start_date (str): The start date of the week (format: 'YYYY-MM-DD').
        Returns:
            list[sqlite3.Row]: List of weekly plan records for the goal.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM weekly_plans WHERE goal_id = ? AND start_date = ?", 
                    (goal_id, week_start_date))
        result = cur.fetchall()
        conn.close()
        return result


    def save_weekly_plan(self, goal_id, week_start_date):
        """
        Save a new weekly plan for a specific goal starting from a given date.
        Args:
            goal_id (int): The ID of the goal.
            week_start_date (str): The start date of the week (format: 'YYYY-MM-DD').
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO weekly_plans (goal_id, start_date) VALUES (?, ?)", 
                    (goal_id, week_start_date))
        conn.commit()
        conn.close()


    def get_tasks_for_date(self, user_id, target_date):
        """
        Retrieve all tasks for a user on a specific date.
        Args:
            user_id (int): The ID of the user.
            target_date (str): The date for which to retrieve tasks (format: 'YYYY-MM-DD').
        Returns:
            list[sqlite3.Row]: List of task records for the given date.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE user_id = ? AND date = ?", (user_id, target_date))
        result = cur.fetchall()
        conn.close()
        return result
    

    def add_custom_task(self, goal_id, day, description):
        """
        Add a custom task for a specific goal on a specific day.
        Args:
            goal_id (int): The ID of the goal.
            day (str): The day for which the task is being added (format: 'YYYY-MM-DD').
            description (str): The description of the task.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        # Insert user_id by looking up the user_id from the goal
        cur.execute("SELECT user_id FROM goals WHERE id = ?", (goal_id,))
        row = cur.fetchone()
        user_id = row['user_id'] if row else None
        cur.execute("""
                    INSERT INTO tasks (user_id, goal_id, day, description, completed, is_custom, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, goal_id, day, description, False, True, day))
        conn.commit()
        conn.close()


    def mark_task_complete(self, task_id):
        """
        Mark a task as complete in the database.
        Args:
            task_id (int): The ID of the task to mark as complete.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()


    def update_task(self, task_id, new_description, new_day=None):
        """
        Update the description and optionally the day of a task in the database.
        Args:
            task_id (int): The ID of the task to update.
            new_description (str): The new description for the task.
            new_day (str, optional): The new day for the task (format: 'YYYY-MM-DD'). Defaults to None.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        if new_day:
            cur.execute("UPDATE tasks SET description = ?, day = ? WHERE id = ?",
                        (new_description, new_day, task_id))
        else:
            cur.execute("UPDATE tasks SET description = ? WHERE id = ?",
                        (new_description, task_id))
        conn.commit()
        conn.close()


    def delete_task(self, task_id):
        """
        Delete a task from the database by its ID.
        Args:
            task_id (int): The ID of the task to delete.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()


    def get_pending_tasks(self, user_id):
        """
        Retrieve all pending (incomplete) tasks for a user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list[sqlite3.Row]: List of pending task records for the user.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT t.* FROM tasks t
                    JOIN goals g ON t.goal_id = g.id
                    WHERE t.user_id = ? AND t.completed = 0
                    """, (user_id,))
        result = cur.fetchall()
        conn.close()
        return result


    def get_completed_tasks(self, user_id):
        """
        Retrieve all completed tasks for a user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            list[sqlite3.Row]: List of completed task records for the user.
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT t.* FROM tasks t
                    JOIN goals g ON t.goal_id = g.id
                    WHERE t.user_id = ? AND t.completed = 1
                    """, (user_id,))
        result = cur.fetchall()
        conn.close()
        return result