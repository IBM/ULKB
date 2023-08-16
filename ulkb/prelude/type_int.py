# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ..commands import *
from ..expression import *
from .bootstrap import *

__all__ = [
    'IntType',
    'ge_z',
    'gt_z',
    'int_',
    'le_z',
    'lt_z',
]


class IntType(TypeApplication):
    constructor = new_type_constructor('int', 0)
    instance = None

    def __new__(                # ()
            cls, **kwargs):
        return cls.constructor(**kwargs)

    @classmethod
    def test(cls, arg):
        return arg == cls.instance

    @classmethod
    def cast(cls, arg):
        return cls.Constant(int(arg), cls())


IntType.instance = IntType()
int_ = IntType.instance
new_python_type_alias(int, int_, IntType)

IntType.ge = Constant('ge_z', FunctionType(int_, int_, bool_))
IntType.gt = Constant('gt_z', FunctionType(int_, int_, bool_))
IntType.le = Constant('le_z', FunctionType(int_, int_, bool_))
IntType.lt = Constant('lt_z', FunctionType(int_, int_, bool_))

ge_z = IntType.ge
gt_z = IntType.gt
le_z = IntType.le
lt_z = IntType.lt
