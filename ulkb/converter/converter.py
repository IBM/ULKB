# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from .. import error
from ..settings import Settings

__all__ = [
    'ConverterError',
    'ConverterSettings',
    'Converter',
]


class ConverterError(error.Error):
    def __init__(self, converter, reason):
        super().__init__(f'{converter.__class__.__name__}: {reason}')
        self.converter = converter
        self.reason = reason


class ConverterSettings(Settings):
    """Converter settings."""

    #: Default converter.
    default = 'ast'


class Converter(ABC):

    converters = dict()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        kwargs['class'] = cls
        format = kwargs['format']
        cls.converters[format] = kwargs
        ConverterSettings._register_attribute(format, kwargs['settings'])

    def __init__(self, cls, arg, **kwargs):
        self.cls = cls
        self.arg = arg

    def error(self, msg):
        return ConverterError(self, msg)

    @abstractmethod
    def do_convert_from(self):
        raise NotImplementedError

    @abstractmethod
    def do_convert_to(self):
        raise NotImplementedError

    @classmethod
    def convert_from(cls, object_cls, value, format=None, **kwargs):
        conv_cls = cls.converters[format]['class']
        return conv_cls(object_cls, value, **kwargs).do_convert_from()

    @classmethod
    def convert_to(cls, object, format=None, **kwargs):
        conv_cls = cls.converters[format]['class']
        return conv_cls(object.__class__, object, **kwargs).do_convert_to()
