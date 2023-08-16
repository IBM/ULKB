# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from . import util
from .converter import ConverterSettings
from .graph.settings import GraphSettings
from .parser import ParserSettings
from .serializer import SerializerSettings
from .settings import Settings

__all__ = [
    'TheorySettings',
]


class TheorySettings(Settings):
    """Theory settings."""

    #: Graph settings.
    graph = GraphSettings

    #: Converter settings.
    converter = ConverterSettings

    #: Parser settings.
    parser = ParserSettings

    #: Serializer settings.
    serializer = SerializerSettings

    #: Prelude settings.
    prelude = None

    #: Prefix of generated ids.
    generated_id_prefix = '_'

    #: Whether to record proofs.
    record_proofs = True

    #: Whether to override :meth:`Object.__repr__`.
    override_object_repr = True

    _debug = False

    @property
    def debug(self):
        """Whether to enable debugging."""
        return self._debug

    @debug.setter
    def debug(self, value):
        util.logging.basicConfig()
        self._debug = bool(value)
        if self._debug:
            util.logging.getLogger().setLevel(util.logging.DEBUG)
        else:
            util.logging.getLogger().setLevel(util.logging.WARNING)
