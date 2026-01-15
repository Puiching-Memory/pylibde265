from . import de265
from . import visualize
from .de265 import decoder, FileDemuxer, isOk, get_error_text, Error as de265_error

import importlib.metadata
__version__ = importlib.metadata.version("pylibde265")
