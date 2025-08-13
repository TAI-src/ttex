from abc import ABC, abstractmethod
class Record(ABC):
    """
    Abstract base class for a record in a file.
    This class defines the structure and methods that all record types must implement.
    """
    @abstractmethod
    def __str__(self) -> str:
        """
        Abstract method to format the record as a string.
        Must be implemented by subclasses.
        
        Returns:
            str: Formatted record string.
        """
        pass

class Header(ABC):
    """
    Abstract base class for a header in a file.
    This class extends Record and defines the structure and methods that all header types must implement.
    """
    @abstractmethod
    def __str__(self) -> str:
        """
        Abstract method to format the header as a string.
        Must be implemented by subclasses.
        
        Returns:
            str: Formatted header string.
        """
        pass

    @property
    @abstractmethod
    def filepath(self) -> str:
        pass

