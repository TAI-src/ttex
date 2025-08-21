from logging import Filter
from ttex.log.record import (
    Header,
)


class COCOHandlerFilter(Filter):
    """
    Filter to allow only COCOHeader and COCORecord messages.
    This filter is used to ensure that only relevant COCO records are processed.
    """

    def __init__(self, key: str, name: str = "COCOHandlerFilter"):
        """
        Initialize the COCOHandlerFilter with an optional name.
        """
        self.key = key
        self.uuid = None
        super().__init__(name)

    def filter(self, record):
        """ """
        if not hasattr(record, self.key):
            return False

        key_record = getattr(record, self.key, None)
        if isinstance(key_record, Header):
            if key_record.uuid == self.uuid:
                # If the UUID is the same, do not log this record
                return False
            self.uuid = key_record.uuid
            return True
        return True
