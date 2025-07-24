from abc import ABC, abstractmethod
from datetime import date


class AbstractDataManager(ABC):
    """
    Abstract base class that defines the interface for data management operations
    in the GoalGPT application.

    Any class that implements this interface (e.g., SQLiteDataManager) must
    provide concrete implementations for all defined methods.

    Responsibilities include:
    - User account creation and retrieval
    - Goal creation and management
    - Weekly plan generation and storage
    - Daily task management (CRUD operations)
    - Tracking task completion status

    This abstraction allows the underlying data storage mechanism (SQLite, 
    PostgreSQL, Firebase, etc.) to be swapped or extended without affecting
    the rest of the application logic.
    """


    @abstractmethod
    def get_user(self, user_id: int):
        pass


    @abstractmethod
    def save_user(self, name: str, email: str, password_hash: str):
        pass


    @abstractmethod
    def get_goals(self, user_id: int):
        pass


    @abstractmethod
    def save_goal(self, user_id: int, goal: dict):
        pass


    @abstractmethod
    def update_goal(self, goal_id: int, new_description: str):
        pass


    @abstractmethod
    def delete_goal(self, goal_id: int):
        pass


    @abstractmethod
    def get_weekly_plan(self, goal_id: int, week_start_date: date):
        pass


    @abstractmethod
    def save_weekly_plan(self, goal_id: int, week_start_date: date):
        pass


    @abstractmethod
    def get_tasks_for_date(self, user_id: int, target_date: date):
        pass


    @abstractmethod
    def mark_task_complete(self, task_id: int):
        pass


    @abstractmethod
    def get_pending_tasks(self, user_id: int):
        pass


    @abstractmethod
    def get_completed_tasks(self, user_id: int):
        pass


    @abstractmethod
    def get_user_by_email(self, email: str):
        pass


    @abstractmethod
    def verify_user(self, email: str, password_hash: str):
        pass