import logging

from .utils.dummy_log_handler import dummy_log_handler, logger

# Suppress DEBUG logs from matplotlib components
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("matplotlib.ticker").setLevel(logging.ERROR)
logging.getLogger("matplotlib.backends.backend_pdf").setLevel(logging.ERROR)
logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)
