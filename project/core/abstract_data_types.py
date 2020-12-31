"""ATD specifications of project."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Union

from project.core.data import BaseData


class AbstractUseCase(ABC):
    """
    Abstract Interface for use cases.
    """

    result_of_execution = None

    def __init__(self, repo=None):
        """Initiate with chosen repo."""
        if repo:
            self.repo = repo

    # Commands:
    # ---------------------------------------------------------------------------
    @abstractmethod
    def set_params(self, *args):
        """Set parameters for use case."""
        pass

    @abstractmethod
    def execute(self):
        """Execute use case logic."""
        pass

    # Queries:
    # ---------------------------------------------------------------------------
    @abstractmethod
    def get_execution_result(self):
        """
        Return data class instance as result of interactor execution.
        """
        return self.result_of_execution


class AbstractRepo(ABC):
    """
    Abstract type for repository pattern.
    """

    database_class: Any
    data_class: BaseData

    def __init__(self, database_class, data_class):
        self.orm_class = database_class
        self.data_class = data_class

    # Commands:
    # ---------------------------------------------------------------------------
    @abstractmethod
    def create(self, **kwargs) -> int:
        """
        Create new object.
        """
        pass

    @abstractmethod
    def update(self, data_instance: BaseData, with_lock: bool = False) -> int:
        """
        data_instance: DataClass
        with_lock: pass True if you want to protect object simultaneous update.
        """
        pass

    @abstractmethod
    def update_incrementally(
        self,
        data_instance: BaseData,
        field: str,
        value: Union[int, Decimal, float],
    ):
        """
        Set new numeric field value based on old field value.
        """
        pass

    # Queries:
    # ---------------------------------------------------------------------------
    @abstractmethod
    def get(self, with_lock: bool = False, **kwargs) -> BaseData:
        """
        Get object from ORM and return dataclass instance.
        with_lock: pass True if you want to protect object simultaneous update.
        """
        pass
