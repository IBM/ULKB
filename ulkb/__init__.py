# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import sys

from . import graph
from .commands import *
from .converter import ConverterError
from .expression import *
from .extension import *
from .object import *
from .parser import ParserError
from .prelude import *
from .rule import *
from .sequent import *
from .serializer import SerializerError
from .theory import *
from .theory_settings import *

Theory._prelude_prefix = __name__
Theory.top._prelude = sys.modules[__name__ + '.prelude']
Theory.top._prelude_offset = len(Theory.top.args)

__version__ = '0.1'

__all__ = [
    'ConverterError',
    'ParserError',
    'SerializerError',
    'graph',
    *commands.__all__,
    *expression.__all__,
    *extension.__all__,
    *object.__all__,
    *prelude.__all__,
    *rule.__all__,
    *sequent.__all__,
    *theory.__all__,
    *theory_settings.__all__,
]
