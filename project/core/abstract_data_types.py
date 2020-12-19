"""ATD specifications of project."""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Iterable, Union


class AbstractData(ABC):
    """
    Base data class instance to use as data objects in all project logic.
    """

    id: int

    @property
    def fields(self) -> Iterable[str]:
        return self.__slots__

    def __init__(self, **kwargs):
        """convert field to field_id to represent Foreign key"""
        for field in self.__slots__:
            field_name = field[:-3] if field.endswith("_id") else field
            setattr(self, field, kwargs[field_name])


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
    data_class: AbstractData

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
    def update(self, data_instance: AbstractData, with_lock: bool = False) -> int:
        """
        data_instance: DataClass
        with_lock: pass True if you want to protect object simultaneous update.
        """
        pass

    @abstractmethod
    def update_incrementally(
        self,
        data_instance: AbstractData,
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
    def get(self, with_lock: bool = False, **kwargs) -> AbstractData:
        """
        Get object from ORM and return dataclass instance.
        with_lock: pass True if you want to protect object simultaneous update.
        """
        pass
