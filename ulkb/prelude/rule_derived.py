# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import util
from ..expression import *
from ..rule import *
from ..sequent import *
from .formula import *
from .rule_primitive import *

__all__ = [
    'AlphaConv',
    'BetaConv',
    'Conversion',
    'FailConv',
    'PassConv',
    'RuleAlpha',
    'RuleAlphaRename',
    'RuleApTerm',
    'RuleApThm',
    'RuleConj',
    'RuleCut',
    'RuleEqTruthElim',
    'RuleEqTruthIntro',
    'RuleSym',
    'RuleTruth',
    'RuleWeaken',
    'TraceConv',
]


class RuleCut(DerivedRule):
    r"""Cut.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤_1 ⊢ p$}
       \AXC{$𝛤_2 ⊢ q$}
       \RL{$\ \small\mathtt{Cut}$}
       \BIC{$𝛤_1 ∪ (𝛤_2 ⧵ \{p\}) ⊢ q$}
       \end{prooftree}

    The interesting case is when :math:`p ∈ 𝛤_2`.

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤_1 ⊢ p`.
       arg2 (:class:`Sequent`): :math:`𝛤_2 ⊢ q`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤_1 ∪ (𝛤_2 ⧵ \{p\}) ⊢ q`.

    See also:
       `PROVE_HYP (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/PROVE_HYP.html>`_.
    """
    @classmethod
    def _new(                # (seq1, seq2)
            cls, arg1, arg2):
        seq1 = Sequent.check(arg1, cls.__name__, None, 1)
        seq2 = Sequent.check(arg2, cls.__name__, None, 2)
        return RuleEqMP(
            RuleDeductAntisym(
                seq1,           # 1. 𝛤_1 ⊢ p
                seq2            # 2. 𝛤_2 ⊢ q
            ),                  # 3. (𝛤_1-{q}) ∪ (𝛤_2-{p}) ⊢ p ↔ q
            seq1                # 4. 𝛤_1 ⊢ p
        )                       # 5. (𝛤_1-{q}) ∪ (𝛤_2-{p}) ⊢ q, by EqMP(3,4)

    @classmethod
    def _test(cls, hs, c):
        return c.is_formula()


class RuleWeaken(DerivedRule):
    r"""Weakening.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ p$}
       \RL{$\ \small\mathtt{RuleWeaken}(q)$}
       \UIC{$𝛤 ∪ \{q\} ⊢ p$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Formula`): :math:`q`.
       arg2 (:class:`Sequent`): :math:`𝛤 ⊢ p`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤 ∪ \{q\} ⊢ p`.
    """
    @classmethod
    def _new(                   # (form, seq)
            cls, arg1, arg2):
        q = Formula.check(arg1, cls.__name__, None, 1)
        return RuleCut(
            RuleAssume(q),      # 1. q ⊢ q
            arg2                # 2. 𝛤 ⊢ p
        )                       # 3. {q} ∪ (𝛤-{q}) ⊢ p

    @classmethod
    def _test(cls, hs, c):
        return bool(hs)         # not empty


# -- Equality --------------------------------------------------------------

class RuleApTerm(DerivedRule):
    r"""Application of term to equality theorem.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ t_1 = t_2$}
       \RL{$\ \small\mathtt{RuleApTerm}(f)$}
       \UIC{$𝛤 ⊢ f\ t_1 = f\ t_2$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Term`): :math:`f`.
       arg2 (:class:`Sequent`): :math:`𝛤 ⊢ t_1 = t_2`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤 ⊢ f\ t_1 = f\ t_2`.

    See also:
       `AP_TERM (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/AP_TERM.html>`_.
    """
    @classmethod
    def _new(                   # (term, seq)
            cls, arg1, arg2):
        f = Term.check(arg1, cls.__name__, None, 1)
        seq = Sequent.check(arg2, cls.__name__, None, 2)
        return RuleMkComb(
            RuleRefl(f),        # 1. ⊢ f = f
            seq                 # 2. 𝛤 ⊢ t1 = t2
        )                       # 3. 𝛤 ⊢ f t1 = f t2, by MkComb(1,2)

    @classmethod
    def _test(cls, hs, c):
        if not c.is_equal():
            return False
        l, r = c._unpack_equal()
        if not l.is_application() or not r.is_application():
            return False
        return l.left == r.left


class RuleApThm(DerivedRule):
    r"""Application of equality theorem to term.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ f = g$}
       \RL{$\ \small\mathtt{RuleApThm}(t)$}
       \UIC{$𝛤 ⊢ f\ t = g\ t$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤 ⊢ f = g`.
       arg2 (:class:`Term`): :math:`t`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤 ⊢ f\ t = g\ t`.

    See also:
       `AP_THM (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/AP_THM.html>`_.
    """
    @classmethod
    def _new(                   # (seq, term)
            cls, arg1, arg2):
        seq = Sequent.check(arg1, cls.__name__, None, 1)
        t = Term.check(arg2, cls.__name__, None, 2)
        return RuleMkComb(
            seq,                # 1. 𝛤 ⊢ f = g
            RuleRefl(t)         # 2. ⊢ t = t
        )                       # 3. 𝛤 ⊢ f t = g t, by MkComb(1,2)

    @classmethod
    def _test(cls, hs, c):
        if not c.is_equal():
            return False
        l, r = c._unpack_equal()
        if not l.is_application() or not r.is_application():
            return False
        return l.right == r.right


class RuleSym(DerivedRule):
    r"""Symmetry of equality.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ t_1 = t_2$}
       \RL{$\ \small\mathtt{RuleSym}$}
       \UIC{$𝛤 ⊢ t_2 = t_1$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤 ⊢ t_1 = t_2`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤 ⊢ t_2 = t_1`.

    See also:
       `SYM (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/SYM.html>`_.
    """
    @classmethod
    def _new(                   # (seq,)
            cls, arg1):
        seq = Sequent.check(arg1, cls.__name__, None, 1)
        _, c = seq._unpack_sequent()
        t1, t2 = cls.asserted_unpack_equal(c)
        return RuleEqMP(
            RuleMkComb(
                RuleApTerm(
                    c.left.left,
                    seq       # 1. 𝛤 ⊢ t1 = t2
                ),            # 2. 𝛤 ⊢ (= t1) = (= t2), by ApTerm(=,1)
                RuleRefl(t1)  # 3. ⊢ t1 = t1
            ),                # 4. 𝛤 ⊢ (t1 = t1) = (t2 = t1), by MkComb(2,3)
            RuleRefl(t1)      # 5. ⊢ t1 = t1
        )                     # 6. 𝛤 ⊢ t2 = t1, by EqMP(4,5)

    @classmethod
    def _test(cls, hs, c):
        return c.is_equal()


class RuleAlpha(DerivedRule):
    r"""Equality of alpha-convertible terms.

    .. math::
       \begin{prooftree}
       \AXC{$\mathstrut$}
       \RL{$\ \small\mathtt{RuleAlpha}(t_1,t_2)$}
       \UIC{$⊢ t_1 = t_2$}
       \end{prooftree}

    Where :math:`t_1 ≡_𝛼 t_2`.

    Parameters:
       arg1 (:class:`Term`): :math:`t_1`.
       arg2 (:class:`Term`): :math:`t_2`.

    Returns:
       :class:`Sequent`:
       :math:`⊢ t_1 = t_2`.

    See also:
       `ALPHA (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/ALPHA_UPPERCASE.html>`_.
    """
    @classmethod
    def _new(                   # (term1, term2)
            cls, arg1, arg2):
        t1 = Term.check(arg1, cls.__name__, None, 1)
        t2 = Term.check(arg2, cls.__name__, None, 2)
        return RuleTrans(
            RuleRefl(t1),       # 1. ⊢ t1 = t1
            RuleRefl(t2)        # 2. ⊢ t2 = t2
        )                       # 3. ⊢ t1 = t2, by RuleTrans(1,2)

    @classmethod
    def _test(cls, hs, c):
        if hs or not c.is_equal():
            return False
        l, r = c._unpack_equal()
        return l == r


class RuleAlphaRename(DerivedRule):
    r"""Alpha-conversion.

    .. math::
       \begin{prooftree}
       \AXC{$\mathstrut$}
       \RL{$\ \small\mathtt{RuleAlphaRename}(y, 𝜆x ⇒ t)$}
       \UIC{$⊢ (𝜆x ⇒ t) = (𝜆y ⇒ t[x≔y])$}
       \end{prooftree}

    Variable :math:`y` must not occur free in :math:`t`.

    Parameters:
       arg1 (:class:`Variable`): :math:`y`.
       arg2 (:class:`Abstraction`): :math:`𝜆x ⇒ t`.

    Returns:
       :class:`Sequent`:
       :math:`⊢ (𝜆x ⇒ t) = (𝜆y ⇒ t[x≔y])`.

    Raises:
       RuleError: :math:`y` occurs free in :math:`t`.

    See also:
       `ALPHA_CONV (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/ALPHA_CONV.html>`_.
    """
    @classmethod
    def _new(                   # (var, term)
            cls, arg1, arg2):
        y = Variable.check(arg1, cls.__name__, None, 1)
        abs = Abstraction.check(arg2, cls.__name__, None, 2)
        x, t = abs._unpack_abstraction()
        if y != x and t.has_free_occurrence_of(y):
            raise cls.error(f"'{y}' occurs free in '{abs}'")
        return RuleAlpha(
            abs,
            abs.rename(y)
        )                       # 1. ⊢ (𝜆 x ⇒ t) = (𝜆 y ⇒ t[x≔v])

    @classmethod
    def _test(cls, hs, c):
        if not RuleAlpha._test(hs, c):
            return False
        l, r = c._unpack_equal()
        if not l.is_abstraction() or not r.is_abstraction():
            return False
        x1, t1 = l._unpack_abstraction()
        x2, t2 = r._unpack_abstraction()
        if x2 != x1 and x2.occurs_free_in([t1]):
            return False
        return t2 == t1.substitute({x1: x2})


# -- Conversion ------------------------------------------------------------

class Conversion:
    """Conversion.

    A conversion is a function that takes a term :math:`t` as input and
    returns and equational theorem :math:`⊢ t = t'` for some :math:`t'`.
    """

    @classmethod
    def _pass(cls):
        return cls(RuleRefl)

    @classmethod
    def _fail(cls):
        def f(t):
            raise Rule.error('fail') from None
        return cls(f)

    __slots__ = (
        '_conv',
    )

    def __init__(self, func):
        self._conv = func

    def __call__(self, *args, **kwargs):
        return self._conv(*args, **kwargs)

    def __invert__(self):
        return self.changed

    def __or__(self, other):
        return self.or_else(other)

    def __rshift__(self, other):
        return self.then(other)

    @property
    def pass_(self):
        return PassConv

    @property
    def fail(self):
        return FailConv

    def trace(self, msg=None):
        def f(t):
            if msg:
                print(f'{msg}: {t}')
            else:
                print(t)
            return PassConv(t)
        return self._then(f)

    def then(self, *convs):
        """<THENC>, <EVERY>"""
        return self._then_rec(iter(convs))

    def _then_rec(self, it):
        try:
            return self._then(next(it)._then_rec(it))
        except StopIteration:
            return self

    def _then(self, conv):
        def f(t):
            seq1 = self(t)
            seq2 = conv(seq1.conclusion.right)
            return Rule.RuleTrans(seq1, seq2)
        return Conversion(f)

    def or_else(self, *convs):
        """<ORELSEC>, <FIRST>"""
        return self._or_else_rec(iter(convs))

    def _or_else_rec(self, it):
        try:
            return self._or_else(next(it)._or_else_rec(it))
        except StopIteration:
            return self

    def _or_else(self, conv):
        def f(t):
            try:
                return self(t)
            except (TypeError, RuleError):
                return conv(t)
        return Conversion(f)

    @property
    def try_(self):
        """<TRY_CONV>"""
        return self.or_else(PassConv)

    @property
    def repeat(self):
        """<REPEATC>"""
        def f(t):
            return self.then(self.repeat).or_else(PassConv)(t)
        return Conversion(f)

    @property
    def changed(self):
        """<CHANGED_CONV>"""
        def f(t):
            seq = self(t)
            l, r = seq.conclusion.unpack_equal()
            return FailConv(t) if l == r else seq
        return Conversion(f)

    @property
    def rw_left(self):
        def f(t):
            l, r = t.unpack_application()
            return RuleApThm(self(l), r)
        return Conversion(f)


PassConv = Conversion._pass()
FailConv = Conversion._fail()
TraceConv = (lambda msg: PassConv.trace(msg))
AlphaConv = (lambda y: Conversion(
    lambda t, **kwargs: RuleAlphaRename(y, t, **kwargs)))
BetaConv = Conversion(RuleBeta)


# -- Truth -----------------------------------------------------------------

class RuleTruth(DerivedRule):
    r"""Truth.

    .. math::
       \begin{prooftree}
       \AXC{$\mathstrut$}
       \RL{$\ \small\mathtt{RuleTruth}$}
       \UIC{$⊢ ⊤$}
       \end{prooftree}

    Returns:
       :class:`Sequent`:
       :math:`⊢ ⊤`.
    """
    @classmethod
    def _new(                   # ()
            cls):
        return RuleEqMP(
            RuleSym(Truth.definition),        # 1. ⊢ (𝜆p ⇒ p) = (𝜆p ⇒ p) ↔ ⊤
            RuleRefl(Truth.definiens.right)   # 2. ⊢ (𝜆p ⇒ p) = (𝜆p ⇒ p)
        )                                     # 3. ⊢ ⊤, by EqMP(1,2)

    @classmethod
    def _test(cls, hs, c):
        return not hs and c == Truth()


class RuleEqTruthIntro(DerivedRule):
    r"""Introduction of equality with truth.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ p$}
       \RL{$\ \small\mathtt{RuleEqTruthIntro}$}
       \UIC{$𝛤 ⊢ p ↔ ⊤$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤 ⊢ p`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤 ⊢ p ↔ ⊤`.

    See also:
       `EQT_INTRO (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/EQT_INTRO.html>`_.
    """
    @classmethod
    def _new(                   # (seq,)
            cls, arg1):
        seq = Sequent.check(arg1, cls.__name__, None, 1)
        if Truth() in seq.hypotheses:
            return RuleWeaken(
                Truth(),
                RuleDeductAntisym(
                    seq,                 # 1. 𝛤,⊤ ⊢ p
                    RuleAssume(Truth())  # 2. ⊤ ⊢ ⊤
                )                        # 3. (𝛤,⊤-{⊤}) ∪ (⊤-{p}) ⊢ p ↔ ⊤
            )                            # 4. 𝛤 ∪ (⊤-{p}) ∪ ⊤ ⊢ p ↔ ⊤
        else:
            return RuleDeductAntisym(
                seq,            # 1. 𝛤 ⊢ p
                RuleTruth()     # 2. ⊢ ⊤
            )                   # 3. (𝛤-{⊤}) ∪ (∅-{p}) ⊢ p ↔ ⊤

    @classmethod
    def _test(cls, hs, c):
        if not c.is_iff():
            return False
        _, r = c._unpack_iff()
        return r.is_truth()


class RuleEqTruthElim(DerivedRule):
    r"""Elimination of equality with truth.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ p ↔ ⊤$}
       \RL{$\ \small\mathtt{RuleEqTruthElim}$}
       \UIC{$𝛤 ⊢ p$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤 ⊢ p ↔ ⊤`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤 ⊢ p`.

    See also:
       `EQT_ELIM (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/EQT_ELIM.html>`_.
    """
    @classmethod
    def _new(                   # (seq,)
            cls, arg1):
        seq = Sequent.check(arg1, cls.__name__, None, 1)
        return RuleEqMP(
            RuleSym(seq),       # 1. 𝛤 ⊢ ⊤ ↔ p
            RuleTruth()         # 2. ⊢ ⊤
        )                       # 3. 𝛤 ⊢ p, by EqMP(1,2)

    @classmethod
    def _test(cls, hs, c):
        return c.is_formula()


# -- And -------------------------------------------------------------------

class RuleConj(PrimitiveRule):
    r"""Conjunction introduction."""

    @classmethod
    def _new(                   # (seq1, seq2)
            cls, arg1, arg2, **kwargs):
        seq1 = Sequent.check(arg1, cls.__name__, None, 1)
        seq2 = Sequent.check(arg2, cls.__name__, None, 2)
        return (seq1.hypotheses | seq2.hypotheses,
                And(seq1.conclusion, seq2.conclusion))
