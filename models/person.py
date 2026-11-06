
from abc import ABC, abstractmethod


class Person(ABC):
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email

    @abstractmethod
    def get_dashboard_name(self):
        pass
