from ttex.log.record import Header
import os
from logging.handlers import BaseRotatingHandler


class ManualRotatingFileHandler(BaseRotatingHandler):
    """
    Custom RotatingFileHandler that allows manual rotation of log files.
    """

    def __init__(self, filepath, mode, encoding=None, errors=None):
        """
        Initialize the handler with the given filename and mode.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        super().__init__(
            filepath, delay=True, mode=mode, encoding=encoding, errors=errors
        )
        self.current_filepath = None
        self.next_filepath = None

    def shouldRollover(self, record):
        """
        Determine if a rollover should occur,
        which is whenever a Header record is logged with a new filepath
        """
        if (
            isinstance(record.msg, Header)
            and record.msg.filepath != self.current_filepath
        ):
            if self.current_filepath is None:
                # This is the first header file,
                # set the current filepath to the first header's filepath
                self.current_filepath = record.msg.filepath
            else:
                assert (
                    self.next_filepath is None
                ), "Next filepath should be None due to previous rollover."
                self.next_filepath = record.msg.filepath
        assert (
            self.current_filepath is not None
        ), "Current filepath should not be None. First message should always be a Header."
        return self.next_filepath is not None

    def doRollover(self):
        """
        Perform the rollover by closing the current stream and renaming the file.
        """
        assert self.current_filepath is not None, "Current filepath should not be None."
        os.makedirs(os.path.dirname(self.current_filepath), exist_ok=True)
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore[assignment]
        self.rotate(self.baseFilename, self.current_filepath)
        self.current_filepath = self.next_filepath
        self.next_filepath = None
        if not self.delay:
            self.stream = self._open()

    def close(self):
        assert (
            self.next_filepath is None
        ), "Next filepath should be None before closing."
        if self.current_filepath is not None:
            # Ensure we perform a rollover if there is a current filepath
            # before closing the handler
            self.doRollover()
        super().close()
