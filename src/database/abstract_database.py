from abc import ABC, abstractmethod
from typing import List, Dict


class Database(ABC):

    @abstractmethod
    def reset_database(self):
        pass

    @abstractmethod
    def create_table(self, name: str, columns: List[str]) -> bool:
        pass
    
    @abstractmethod
    def get_all_table_names(self):
        pass

    @abstractmethod
    def insert_row(self, tableName: str, values: Dict[str, str]):
        pass
    
    @abstractmethod
    def delete_row(self, tableName: str, id: str):
        pass
