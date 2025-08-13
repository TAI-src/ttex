import logging
from ttex.log.record import Header
import os

class ManualRotatingFileHandler(logging.handlers.BaseRotatingHandler):
    """
    Custom RotatingFileHandler that allows manual rotation of log files.
    """
    def __init__(self, filepath, mode, encoding=None, errors=None):
        """
        Initialize the handler with the given filename and mode.
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        super().__init__(filepath, delay=True, mode=mode, encoding=encoding, errors=errors)
        self.rotation_filepaths = []


    def shouldRollover(self, record):
        """
        Determine if a rollover should occur, which is whenever a Header record is logged.
        """
        should_rollover = False
        if isinstance(record.msg, Header):
            self.rotation_filepaths.append(record.msg.filepath) # Store the filepath for rotation
            if len(self.rotation_filepaths) > 1:
                # If this is not the first Header, we should rollover
                should_rollover = True
        assert len(self.rotation_filepaths) <= 2, "Only max 2 rotation filepath should be stored at a time."
        assert len(self.rotation_filepaths) > 0, "No header record has been logged yet. Please log a Header record before emitting other records."
        return should_rollover

    def doRollover(self):
        """
        Perform the rollover by closing the current stream and renaming the file.
        """
        filepath = self.rotation_filepaths.pop(0)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if self.stream:
            self.stream.close()
            self.stream = None
        self.rotate(self.baseFilename, filepath)
        if not self.delay:
            self.stream = self._open()

    def close(self):
        assert len(self.rotation_filepaths) == 1, "Handler should be closed with exactly one rotation filepath remaining."
        self.doRollover()
        super().close()
 
