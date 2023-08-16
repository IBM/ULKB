# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ..expression import *
from ..rule import *
from ..sequent import *
from .bootstrap import *
from .formula import *

__all__ = [
    'RuleAssume',
    'RuleRefl',
    'RuleTrans',
    'RuleMkComb',
    'RuleAbs',
    'RuleBeta',
    'RuleEqMP',
    'RuleDeductAntisym',
    'RuleInstType',
    'RuleSubst',
]


class RuleAssume(PrimitiveRule):
    r"""Assumption introduction.

    .. math::
       \begin{prooftree}
       \AXC{$\mathstrut$}
       \RL{$\ \small\mathtt{RuleAssume}(p)$}
       \UIC{$p ⊢ p$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Formula`): :math:`p`.
       kwargs: Annotations.

    Returns:
       :class:`Sequent`:
       :math:`p ⊢ p`.

    See also:
       `ASSUME (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/ASSUME.html>`_.
    """
    @classmethod
    def _new(                   # (form,)
            cls, arg1):
        form = Formula.check(arg1, cls.__name__, None, 1)
        return {form}, form

    @classmethod
    def _test(cls, hs, c):
        return c.is_formula() and hs == {c}


class RuleRefl(PrimitiveRule):
    r"""Reflexivity of equality.

    .. math::
       \begin{prooftree}
       \AXC{$\mathstrut$}
       \RL{$\ \small\mathtt{RuleRefl}(t)$}
       \UIC{$⊢ t = t$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Term`): :math:`t`.
       kwargs: Annotations.

    Returns:
       :class:`Sequent`:
       :math:`⊢ t = t`.

    See also:
       `REFL (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/REFL.html>`_.
    """
    @classmethod
    def _new(                   # (term,)
            cls, arg1):
        term = Term.check(arg1, cls.__name__, None, 1)
        return set(), Equal(term, term)

    @classmethod
    def _test(cls, hs, c):
        if hs or not c.is_equal():
            return False
        l, r = c._unpack_equal()
        return l == r


class RuleTrans(PrimitiveRule):
    r"""Transitivity of equality.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤_1 ⊢ t_1 = t$}
       \AXC{$𝛤_2 ⊢ t = t_2$}
       \RL{$\ \small\mathtt{RuleTrans}$}
       \BIC{$𝛤_1 ∪ 𝛤_2 ⊢ t_1 = t_2$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤_1 ⊢ t_1 = t`.
       arg2 (:class:`Sequent`): :math:`𝛤_2 ⊢ t = t_2`.
       kwargs: Annotations.

    Returns:
       :class:`Sequent`:
       :math:`𝛤_1 ∪ 𝛤_2 ⊢ t_1 = t_2`.

    Raises:
       RuleError: Unexpected format for `arg1` or `arg2`.

    See also:
       `TRANS (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/TRANS.html>`_.
    """
    @classmethod
    def _new(                   # (seq1, seq2)
            cls, arg1, arg2):
        seq1 = Sequent.check(arg1, cls.__name__, None, 1)
        seq2 = Sequent.check(arg2, cls.__name__, None, 2)
        hs1, c1 = seq1._unpack_sequent()
        hs2, c2 = seq2._unpack_sequent()
        l1, r1 = cls.asserted_unpack_equal(c1)
        l2, r2 = cls.asserted_unpack_equal(c2)
        cls.assert_equal(r1, l2)  # alpha-equal
        return hs1 | hs2, Equal(l1, r2)

    @classmethod
    def _test(cls, hs, c):
        return c.is_equal()


class RuleMkComb(PrimitiveRule):
    r"""Equality of applications.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤_1 ⊢ f = g$}
       \AXC{$𝛤_2 ⊢ t_1 = t_2$}
       \RL{$\ \small\mathtt{RuleMkComb}$}
       \BIC{$𝛤_1 ∪ 𝛤_2 ⊢ f\ t_1 = g\ t_2$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤_1 ⊢ f = g`.
       arg2 (:class:`Sequent`): :math:`𝛤_2 ⊢ t_1 = t_2`.
       kwargs: Annotations.

    Returns:
       :class:`Sequent`:
       :math:`𝛤_1 ∪ 𝛤_2 ⊢ f\ t_1 = g\ t_2`.

    Raises:
       RuleError: Unexpected format for `arg1` or `arg2`.

    See also:
       `MK_COMB (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/MK_COMB_UPPERCASE.html>`_.
    """
    @classmethod
    def _new(                   # (seq1, seq2)
            cls, arg1, arg2):
        seq1 = Sequent.check(arg1, cls.__name__, None, 1)
        seq2 = Sequent.check(arg2, cls.__name__, None, 2)
        hs1, c1 = seq1._unpack_sequent()
        hs2, c2 = seq2._unpack_sequent()
        l1, r1 = cls.asserted_unpack_equal(c1)
        l2, r2 = cls.asserted_unpack_equal(c2)
        cls.assert_can_apply(r1, r2)  # if succeeds, (l1 l2) will succeed
        return hs1 | hs2, Equal(l1(l2), r1(r2))

    @classmethod
    def _test(cls, hs, c):
        return (c.is_equal()
                and c.left.is_application()
                and c.right.is_application())


class RuleAbs(PrimitiveRule):
    r"""Abstraction of equality.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ t_1=t_2$}
       \RL{$\ \small\mathtt{RuleAbs}(x)$}
       \UIC{$𝛤 ⊢ (𝜆x ⇒ t_1)=(𝜆x ⇒ t_2)$}
       \end{prooftree}

    Variable :math:`x` must not occur free in :math:`𝛤`.

    Parameters:
       arg1 (:class:`Variable`): :math:`x`.
       arg2 (:class:`Sequent`): :math:`𝛤 ⊢ t_1=t_2`.
       kwargs: Annotations.

    Returns:
       :class:`Sequent`:
       :math:`𝛤 ⊢ (𝜆x ⇒ t_1) = (𝜆x ⇒ t_2)`.

    Raises:
       RuleError: :math:`x` occurs free in :math:`𝛤`.
       RuleError: Unexpected format for `arg2`.

    See also:
       `ABS (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/ABS.html>`_.
    """
    @classmethod
    def _new(                   # (var, seq)
            cls, arg1, arg2):
        x = Variable.check(arg1, cls.__name__, None, 1)
        seq = Sequent.check(arg2, cls.__name__, None, 2)
        hs, c = seq._unpack_sequent()
        l, r = cls.asserted_unpack_equal(c)
        for h in hs:
            if h.has_free_occurrence_of(x):
                raise cls.error(f"'{x}' occurs free in hypothesis '{h}'")
        return hs, Equal(x >> l, x >> r)

    @classmethod
    def _test(cls, hs, c):
        if not c.is_equal():
            return False
        l, r = c._unpack_equal()
        if not l.is_abstraction() or not r.is_abstraction():
            return False
        x1, _ = l._unpack_abstraction()
        x2, _ = r._unpack_abstraction()
        return x1 == x2 and not x1.occurs_free_in(hs)


class RuleBeta(PrimitiveRule):
    r"""Beta-conversion primitive.

    .. math::
       \begin{prooftree}
       \AXC{$\mathstrut$}
       \RL{$\ \small\mathtt{RuleBeta}((𝜆x ⇒ t_1)\ t_2)$}
       \UIC{$⊢ (𝜆x ⇒ t_1)\ t_2 = t_1[x≔t_2]$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`BetaRedex`): :math:`(𝜆x ⇒ t_1)\ t_2`.

    Returns:
       :class:`Sequent`:
       :math:`⊢ (𝜆x ⇒ t_1)\ t_2 = t_1[x≔t_2]`.

    See also:
       `BETA_CONV (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/BETA_CONV.html>`_.
    """
    @classmethod
    def _new(                   # (term,)
            cls, arg1, **kwargs):
        app = BetaRedex.check(arg1, cls.__name__, None, 1)
        abs, t = app._unpack_beta_redex()
        return set(), Equal(app, abs[1].close(t))

    @classmethod
    def _test(cls, hs, c):
        if hs or not c.is_equal():
            return False
        l, r = c._unpack_equal()
        if not l.is_beta_redex():
            return False
        abs, t = l._unpack_beta_redex()
        return abs[1].close(t) == r


class RuleEqMP(PrimitiveRule):
    r"""Equivalence elimination.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤_1 ⊢ p ↔ q$}
       \AXC{$𝛤_2 ⊢ p$}
       \RL{$\ \small\mathtt{RuleEqMP}$}
       \BIC{$𝛤_1 ∪ 𝛤_2 ⊢ q$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤_1 ⊢ p ↔ q`.
       arg2 (:class:`Sequent`): :math:`𝛤_2 ⊢ p`.

    Returns:
       :class:`Sequent`:
       :math:`𝛤_1 ∪ 𝛤_2 ⊢ q`.

    Raises:
       RuleError: Unexpected format for `arg1` or `arg2`.

    See also:
       `EQ_MP (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/EQ_MP.html>`_.
    """
    @classmethod
    def _new(                # (seq1, seq2)
            cls, arg1, arg2, **kwargs):
        seq1 = Sequent.check(arg1, cls.__name__, None, 1)
        seq2 = Sequent.check(arg2, cls.__name__, None, 2)
        hs1, c1 = seq1._unpack_sequent()
        hs2, c2 = seq2._unpack_sequent()
        l, r = cls.asserted_unpack_iff(c1)
        cls.assert_equal(l, c2)  # alpha-equal
        return hs1 | hs2, r

    @classmethod
    def _test(cls, hs, c):
        return c.is_formula()


class RuleDeductAntisym(PrimitiveRule):
    r"""Equivalence introduction.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤_1 ⊢ p$}
       \AXC{$𝛤_2 ⊢ q$}
       \RL{$\ \small\mathtt{RuleDeductAntisym}$}
       \BIC{$(𝛤_1 ⧵ \{q\}) ∪ (𝛤_2 ⧵ \{p\}) ⊢ p ↔ q$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`Sequent`): :math:`𝛤_1 ⊢ p`.
       arg2 (:class:`Sequent`): :math:`𝛤_2 ⊢ q`.

    Returns:
       :class:`Sequent`:
       :math:`(𝛤_1 ⧵ \{q\}) ∪ (𝛤_2 ⧵ \{p\}) ⊢ p ↔ q`.

    Raises:
       RuleError: Unexpected format for `arg1` or `arg2`.

    See also:
       `DEDUCT_ANTISYM_RULE (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/DEDUCT_ANTISYM_RULE.html>`_.
    """
    @classmethod
    def _new(                   # (seq1, seq2)
            cls, arg1, arg2):
        seq1 = Sequent.check(arg1, cls.__name__, None, 1)
        seq2 = Sequent.check(arg2, cls.__name__, None, 2)
        hs1, c1 = seq1._unpack_sequent()
        hs2, c2 = seq2._unpack_sequent()
        return (hs1 - {c2}) | (hs2 - {c1}), Equal(c1, c2)

    @classmethod
    def _test(cls, hs, c):
        return c.is_iff()


class RuleInstType(PrimitiveRule):
    r"""Type-variable instantiation.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ t$}
       \RL{$\ \small\mathtt{RuleInstType}(𝜃)$}
       \UIC{$𝜃(𝛤) ⊢ 𝜃(t)$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`dict`): Type-variable instantiation :math:`𝜃`.
       arg2 (:class:`Sequent`): :math:`𝛤 ⊢ t`.

    Returns:
       :class:`Sequent`:
       :math:`𝜃(𝛤) ⊢ 𝜃(t)`.

    See also:
       `INST_TYPE (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/INST_TYPE.html>`_.
    """
    @classmethod
    def _new(                   # (theta, seq)
            cls, arg1, arg2):
        theta = arg1
        seq = Sequent.check(arg2, cls.__name__, None, 2)
        hs, c = seq._unpack_sequent()
        return (
            set(map(lambda x: x.instantiate(theta), hs)),
            c.instantiate(theta))

    @classmethod
    def _test(cls, hs, c):
        return c.is_formula()


class RuleSubst(PrimitiveRule):
    r"""Free-variable substitution.

    .. math::
       \begin{prooftree}
       \AXC{$𝛤 ⊢ t$}
       \RL{$\ \small\mathtt{RuleSubst}(𝜃)$}
       \UIC{$𝜃(𝛤) ⊢ 𝜃(t)$}
       \end{prooftree}

    Parameters:
       arg1 (:class:`dict`): Free-variable substitution :math:`𝜃`.
       arg2 (:class:`Sequent`): :math:`𝛤 ⊢ t`.

    Returns:
       :class:`Sequent`:
       :math:`𝜃(𝛤) ⊢ 𝜃(t)`.

    See also:
       `INST (HOL Light)
       <https://www.cl.cam.ac.uk/~jrh13/hol-light/HTML/INST_UPPERCASE.html>`_.
    """
    @classmethod
    def _new(                   # (theta, seq)
            cls, arg1, arg2):
        theta = arg1
        seq = Sequent.check(arg2, cls.__name__, None, 2)
        hs, c = seq._unpack_sequent()
        return (
            set(map(lambda x: x.substitute(theta), hs)),
            c.substitute(theta))

    @classmethod
    def _test(cls, hs, c):
        return c.is_formula()
