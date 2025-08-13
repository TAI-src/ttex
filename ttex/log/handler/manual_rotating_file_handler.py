import logging
from ttex.log.record import Header

class ManualRotatingFileHandler(logging.handlers.BaseRotatingHandler):
    """
    Custom RotatingFileHandler that allows manual rotation of log files.
    """
    def __init__(self, mode, encoding=None, errors=None):
        """
        Initialize the handler with the given filename and mode.
        """
        self.current_file = "dummy_file.txt"
        super().__init__(self.current_file, delay=True, mode=mode, encoding=encoding, errors=errors)
        self.rotation_filepath = None

    def shouldRollover(self, record):
        """
        Determine if a rollover should occur.
        This method can be overridden to change the rollover logic.
        """
        if isinstance(record.msg, Header):
            self.rotation_filepath = record.msg.filepath
            return True
        return False


    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.rotate(self.current_file, self.rotation_filepath)
        self.current_file = self.rotation_filepath
        if not self.delay:
            self.stream = self._open()


 
