import logging
import json
from typing import Optional


class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.

    Attributes:
        fmt_dict (dict): Key: logging format attribute pairs. Defaults to {"message": "message"}.
        time_format (str): time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
        msec_format (str): Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
    """

    def __init__(
        self,
        fmt_dict: Optional[dict] = None,
        time_format: str = "%Y-%m-%dT%H:%M:%S",
        msec_format: str = "%s.%03dZ",
    ):
        """
        Initialize the JsonFormatter with the given format dictionary, time format, and microsecond format.

        Args:
            fmt_dict (Optional[dict]): Key: logging format attribute pairs. Defaults to {"message": "message"}.
            time_format (str): time.strftime() format string. Default: "%Y-%m-%dT%H:%M:%S"
            msec_format (str): Microsecond formatting. Appended at the end. Default: "%s.%03dZ"
        """
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        """
        Check if the formatter uses time.

        Returns:
            bool: True if "asctime" is in the format dictionary values, False otherwise.
        """
        return "asctime" in self.fmt_dict.values()

    def _formatMessage(self, record) -> dict:
        """
        Format the LogRecord into a dictionary.

        Args:
            record (LogRecord): The log record to format.

        Returns:
            dict: A dictionary of the relevant LogRecord attributes.
        """
        return {
            fmt_key: record.__dict__[fmt_val]
            for fmt_key, fmt_val in self.fmt_dict.items()
        }

    def format(self, record) -> str:
        """
        Format the LogRecord as a JSON string.

        Args:
            record (LogRecord): The log record to format.

        Returns:
            str: The formatted log record as a JSON string.
        """
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self._formatMessage(record)

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict, default=str)
