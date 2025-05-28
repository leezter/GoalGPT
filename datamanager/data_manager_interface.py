from abc import ABC, abstractmethod


class AbstractDataManager(ABC):
    """
    Abstract base class for data management operations in the application.
    This class defines the interface for user, goal, and task data operations 
    that concrete data manager implementations must provide.
    """


    @abstractmethod
    def get_user(self, user_id: int):
        pass


    @abstractmethod
    def save_goal(self, user_id: int, goal: dict):
        pass


    @abstractmethod
    def get_tasks_for_date(self, user_id: int, target_date):
        pass


