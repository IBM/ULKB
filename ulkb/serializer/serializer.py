# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from .. import error
from ..settings import Settings

__all__ = [
    'SerializerError',
    'SerializerSettings',
    'Serializer',
]


class SerializerError(error.Error):
    def __init__(self, serializer, reason):
        super().__init__(f'{serializer.__class__.__name__}: {reason}')
        self.serializer = serializer
        self.reason = reason


class SerializerSettings(Settings):
    """Serializer settings."""

    #: Default serializer.
    default = 'ulkb'

    #: Whether to use append-mode when serializing to file.
    append = False


class Serializer(ABC):

    serializers = dict()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        kwargs['class'] = cls
        format = kwargs['format']
        cls.serializers[format] = kwargs
        SerializerSettings._register_attribute(format, kwargs['settings'])

    def __init__(self, obj, encoding=None, **kwargs):
        self.cls = obj.__class__
        self.obj = obj
        self.encoding = encoding or 'utf-8'

    def error(self, msg):
        return SerializerError(self, msg)

    def do_serialize_to_file(self, path):
        mode = 'ab' if self.settings.append else 'wb'
        with open(path, mode) as fp:
            self.do_serialize_to_stream(fp)

    def do_serialize_to_string(self):
        import io
        stream = io.BytesIO()
        self.do_serialize_to_stream(stream)
        return stream.getvalue().decode(self.encoding)

    @abstractmethod
    def do_serialize_to_stream(self, stream):
        raise NotImplementedError

    @classmethod
    def serialize(cls, obj, to=None, format=None, **kwargs):
        serializer = cls.serializers[format]['class'](obj, **kwargs)
        if to is None:
            return serializer.do_serialize_to_string()
        elif hasattr(to, 'write'):
            return serializer.do_serialize_to_stream(to)
        else:
            return serializer.do_serialize_to_file(to)
