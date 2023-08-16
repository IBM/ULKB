# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ..commands import *
from ..expression import *
from .bootstrap import *

__all__ = [
    'RealType',
    'ge_r',
    'gt_r',
    'le_r',
    'lt_r',
    'real',
]


class RealType(TypeApplication):
    constructor = new_type_constructor('real', 0)
    instance = None

    def __new__(                # ()
            cls, **kwargs):
        return cls.constructor(**kwargs)

    @classmethod
    def test(cls, arg):
        return arg == cls.instance

    @classmethod
    def cast(cls, arg):
        return cls.Constant(float(arg), cls())


RealType.instance = RealType()
real = RealType.instance
new_python_type_alias(float, real, RealType)

RealType.ge = Constant('ge_r', FunctionType(real, real, bool_))
RealType.gt = Constant('gt_r', FunctionType(real, real, bool_))
RealType.le = Constant('le_r', FunctionType(real, real, bool_))
RealType.lt = Constant('lt_r', FunctionType(real, real, bool_))

ge_r = RealType.ge
gt_r = RealType.gt
le_r = RealType.le
lt_r = RealType.lt
