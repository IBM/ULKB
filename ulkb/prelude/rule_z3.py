# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ..rule import *
from ..settings import Settings
from .formula import *

__all__ = [
    'RuleZ3',
]


class RuleZ3_Settings(Settings):
    """RuleZ3 settings"""


class RuleZ3(PrimitiveRule, settings=RuleZ3_Settings):

    @classmethod
    def _new(                   # (form,)
            cls, arg1, timeout=None, **kwargs):
        import z3
        conj = Formula.check(arg1, cls.__name__, None, 1)
        conj_z3 = conj.to_z3()
        solver = cls._thy().to_z3()
        if timeout is not None:
            solver.set('timeout', int(timeout))
        if solver.check(z3.Not(conj_z3)) == z3.unsat:
            return {}, conj
        else:
            raise cls.error(f"failed to prove '{conj}'")
