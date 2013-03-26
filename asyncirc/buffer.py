__all__ = ['LineBuffer']

import re

class LineBuffer(object):
    line_sep_exp = re.compile('\r?\n')

    def __init__(self):
        self.buffer = ''

    def feed(self, data):
        self.buffer += data

    def lines(self):
        lines = self.line_sep_exp.split(self.buffer)
        self.buffer = lines.pop()
        return iter(lines)

    def __iter__(self):
        return self.lines()

    def __len__(self):
        return len(self.buffer)

