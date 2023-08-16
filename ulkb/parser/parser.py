# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from .. import error
from ..settings import Settings

__all__ = [
    'ParserError',
    'ParserSettings',
    'Parser',
]


class ParserError(error.Error):
    def __init__(self, parser, reason):
        super().__init__(f'{parser.__class__.__name__}: {reason}')
        self.parser = parser
        self.reason = reason


class ParserSyntaxError(ParserError):

    def __init__(self, parser, line, column, context):
        super().__init__(
            parser, f'at line {line}, column {column}\n\n{context}')
        self.line = line
        self.column = column
        self.context = context


class ParserSettings(Settings):
    """Parser settings."""

    #: Default parser.
    default = 'ulkb'


class Parser(ABC):

    parsers = dict()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        kwargs['class'] = cls
        format = kwargs['format']
        cls.parsers[format] = kwargs
        ParserSettings._register_attribute(format, kwargs['settings'])

    def __init__(self, cls, encoding=None, **kwargs):
        self.cls = cls
        self.encoding = encoding or 'utf-8'

    def error(self, msg):
        return ParserError(self, msg)

    def syntax_error(self, line, column, context):
        return ParserSyntaxError(self, line, column, context)

    def do_parse_from_file(self, path):
        with open(path, 'rb') as fp:
            return self.do_parse_from_stream(fp)

    @abstractmethod
    def do_parse_from_string(self, text):
        raise NotImplementedError

    def do_parse_from_stream(self, stream):
        return self.do_parse_from_string(
            stream.read().decode(self.encoding))

    @classmethod
    def parse(
            cls, object_cls, from_=None, path=None, format=None, **kwargs):
        parser = cls.parsers[format]['class'](object_cls, **kwargs)
        if isinstance(from_, str):
            return parser.do_parse_from_string(from_)
        elif hasattr(from_, 'read'):
            return parser.do_parse_from_stream(from_)
        else:
            return parser.do_parse_from_file(from_ or path)
