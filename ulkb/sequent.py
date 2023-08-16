# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from . import error
from .expression import *
from .object import *

__all__ = [
    'Sequent',
]


class Sequent(Object):
    """Abstract base class for sequents.

    A sequent :math:`𝛤 ⊢ t` represents the hypothetical assertion that the
    set of :attr:`hypotheses` :math:`𝛤` entails the :attr:`conclusion`
    :math:`t`.

    The only way of constructing sequents is using :class:`Rule`'s.
    """
    __slots__ = (
        '_cached_proof',
    )

    def _dump(self, _f=lambda x: x.dump()):
        hs = ' '.join(map(_f, sorted(self[0])))
        return f'({self.__class__.__name__} {hs} {self[1].dump()})'

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:
            return frozenset(map(
                lambda x: self._preprocess_arg_formula(self, x, 1), arg))
        elif i == 2:
            return self._preprocess_arg_formula(self, arg, i)
        else:
            error.should_not_get_here()

    @property
    def hypotheses(self):
        """Sequent hypotheses."""
        return self.get_hypotheses()

    def get_hypotheses(self):
        """Gets the hypotheses of sequent.

        Returns:
           Set of hypotheses.
        """
        return self[0]

    @property
    def conclusion(self):
        """Sequent conclusion."""
        return self.get_conclusion()

    def get_conclusion(self):
        """Gets the conclusion of sequent.

        Returns:
           Conclusion.
        """
        return self[1]

    def _build_proof_cache(self):
        """Gets the proof certificate associated with sequent."""
        if not hasattr(self, '_proof'):
            return None
        cls, args = self._proof
        return (
            cls.__name__,
            *map(lambda x: x.proof if Sequent.test(x) else x, args))


class _Sequent(Sequent):
    def __init__(               # (hypotheses, conclusion)
            self, arg1, arg2, **kwargs):
        super().__init__(arg1, arg2, **kwargs)
