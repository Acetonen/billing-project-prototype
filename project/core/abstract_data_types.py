from abc import ABC, abstractmethod


class AbstractUseCase(ABC):
    """Abstract Interface for use cases."""

    result_of_execution = None

    def __init__(self, repo=None):
        """Initiate with chosen repo."""
        if repo:
            self.repo = repo

    @abstractmethod
    def set_params(self, *args):
        """Set parameters for use case."""
        pass

    @abstractmethod
    def execute(self):
        """Execute use case logic."""
        pass

    @abstractmethod
    def get_execution_result(self):
        """
        Return data class instance as result of interactor execution.
        """
        return self.result_of_execution
