

from .buffer    import *
from .client    import *

__all__ = (buffer.__all__ + client.__all__)

#monkey!~monkey@66.9.128.66
def prefix_nick(prefix):
    return prefix.split('!')[0]
