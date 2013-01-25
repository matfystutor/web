from .base import *

try:
    from .local import *
except ImportError:
    import logging
    logging.warning("Could not import local config.")
