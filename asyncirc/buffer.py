"""A simple buffer that splits into lines"""

__all__ = ['LineBuffer']

import re

class LineBuffer:
    _line_sep = re.compile('\r?\n')

    def __init__(self):
        self._buffer = ''

    def __iter__(self):
        return self.lines()

    def __len__(self):
        return len(self._buffer)

    def push(self, data):
        self._buffer += data

    def lines(self):
        lines = self._line_sep.split(self._buffer)
        self._buffer = lines.pop()
        return iter(lines)

