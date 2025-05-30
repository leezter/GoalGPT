import unittest
import sqlite3
from data_manager import SQLiteDataManager

class TestSQLiteDataManager(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite DB for testing
        self.manager = SQLiteDataManager(':memory:')
        self._create_tables()

    def _create_tables(self):
        cur = self.manager.conn.cursor()
        cur.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password_hash TEXT)''')
        cur.execute('''CREATE TABLE goals (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, description TEXT)''')
        cur.execute('''CREATE TABLE weekly_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, goal_id INTEGER, start_date TEXT)''')
        cur.execute('''CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, goal_id INTEGER, day TEXT, description TEXT, completed INTEGER, is_custom INTEGER, date TEXT)''')
        self.manager.conn.commit()

    def test_save_and_get_user(self):
        self.manager.save_user('Alice', 'alice@example.com', 'hash')
        user = self.manager.get_user(1)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'Alice')

    def test_save_and_get_goal(self):
        self.manager.save_user('Bob', 'bob@example.com', 'hash')
        self.manager.save_goal(1, 'Learn Python')
        goals = self.manager.get_goals(1)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]['description'], 'Learn Python')

    def test_save_and_get_weekly_plan(self):
        self.manager.save_user('Carol', 'carol@example.com', 'hash')
        self.manager.save_goal(1, 'Read Books')
        self.manager.save_weekly_plan(1, '2025-05-26')
        plans = self.manager.get_weekly_plan(1, '2025-05-26')
        self.assertEqual(len(plans), 1)

    def test_add_and_get_task(self):
        self.manager.save_user('Dan', 'dan@example.com', 'hash')
        self.manager.save_goal(1, 'Exercise')
        self.manager.add_custom_task(1, '2025-05-30', 'Run 5km')
        tasks = self.manager.get_tasks_for_date(1, '2025-05-30')
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['description'], 'Run 5km')

    def test_mark_task_complete(self):
        self.manager.save_user('Eve', 'eve@example.com', 'hash')
        self.manager.save_goal(1, 'Meditate')
        self.manager.add_custom_task(1, '2025-05-30', 'Morning meditation')
        self.manager.mark_task_complete(1)
        cur = self.manager.conn.cursor()
        cur.execute('SELECT completed FROM tasks WHERE id = 1')
        completed = cur.fetchone()['completed']
        self.assertEqual(completed, 1)

if __name__ == '__main__':
    unittest.main()
