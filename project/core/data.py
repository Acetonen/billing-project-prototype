from typing import Iterable

from pydantic.main import BaseModel


class BaseData(BaseModel):
    """
    Base data class instance to use as data objects in all project logic.
    """

    id: int

    @property
    def fields(self) -> Iterable[str]:
        return self.__dict__.keys()
