# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ..commands import *
from ..expression import *
from .bootstrap import *

__all__ = [
    'StrType',
    'str_',
]


class StrType(TypeApplication):
    constructor = new_type_constructor('str', 0)
    instance = None

    def __new__(                # ()
            cls, **kwargs):
        return cls.constructor(**kwargs)

    @classmethod
    def test(cls, arg):
        return arg == cls.instance

    @classmethod
    def cast(cls, arg):
        return cls.Constant(str(arg), cls())


StrType.instance = StrType()
str_ = StrType.instance
new_python_type_alias(str, str_, StrType)
