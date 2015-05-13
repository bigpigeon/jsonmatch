__version__ = '0.1.0'
VERSION = tuple(map(int, __version__.split('.')))
from single import (
    filter_with_single

)
from multiple import (
    filter_with_multiple
)

import common
import error

__all__ = ["filter_with_single", "filter_with_multiple"]
# from jsonmatch.single import filter_with_single
# from jsonmatch.multiple import filter_with_multiple
