# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from abc import abstractclassmethod

from . import error, util
from .expression import Term
from .sequent import Sequent, _Sequent
from .settings import Settings

__all__ = [
    'DerivedRule',
    'PrimitiveRule',
    'Rule',
    'RuleError',
]


class RuleError(error.Error):
    """Raised on rule application errors.

    Parameters:
       rule: :class:`Rule`.
       reason: Message.

    Returns:
       A new :class:`RuleError`.
    """

    def __init__(self, rule, reason):
        super().__init__(f'{rule.__name__}: {reason}')
        self.rule = rule
        self.reason = reason


class Rule(Sequent):
    """Abstract base class for rules."""

    def __init_subclass__(cls, **kwargs):
        if 'test' not in cls.__dict__:
            setattr(cls, 'test', classmethod(
                lambda x, arg: (
                    Sequent.test(arg)
                    and x._test(*arg._unpack_sequent()))))

    @classmethod
    def test(cls, arg):
        """Tests whether `arg` is an instance of this rule.

        Parameters:
           arg: Value.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return util.any_map(lambda x: x.test(arg), cls.__subclasses__())

    @abstractclassmethod
    def _test(cls, hs, c):
        raise NotImplementedError

    @classmethod
    def error(cls, msg):
        """Returns a new :class:`RuleError` with `msg`.

        Parameters:
           msg: Message.

        Returns:
           A new :class:`RuleError`.
        """
        return RuleError(cls, msg)

    @classmethod
    def assert_can_apply(cls, arg1, arg2):
        """Checks whether `arg1` can be applied to `arg2`.

        Parameters:
           arg1: :class:`Term`.
           arg2: :class:`Term`.

        Raises:
           RuleError: `arg1` cannot be applied to `arg2`.
        """
        if arg1.type.is_function_type():
            dom, _ = arg1.type.unpack_function_type()
            if dom == arg2.type:
                return True
        raise cls.error(f"cannot apply '{arg1}' to '{arg2}'")

    @classmethod
    def assert_equal(cls, arg1, arg2):
        """Checks whether `arg1` and `arg2` are (alpha) equal.

        Parameters:
           arg1: :class:`Term`.
           arg2: :class:`Term`.

        Raises:
           RuleError: `arg1` and `arg2` are not (alpha) equal.
        """
        if arg1 == arg2:
            return True
        raise cls.error(f"'{arg1}' and '{arg2}' are not (alpha) equal")


_assertions = {
    'variable': (
        lambda x: x.is_variable(),
        lambda x: x._unpack_variable(),
        lambda x: f"'{x}' is not a variable",
    ),
    'constant': (
        lambda x: x.is_constant(),
        lambda x: x._unpack_constant(),
        lambda x: f"'{x}' is not a constant",
    ),
    'application': (
        lambda x: x.is_application(),
        lambda x: x._unpack_application(),
        lambda x: f"'{x}' is not an application",
    ),
    'beta_redex': (
        lambda x: x.is_beta_redex(),
        lambda x: x._unpack_beta_redex(),
        lambda x: f"'{x}' is not a beta-redex",
    ),
    'abstraction': (
        lambda x: x.is_abstraction(),
        lambda x: x._unpack_abstraction(),
        lambda x: f"'{x}' is not an abstraction",
    ),
    'formula': (
        lambda x: x.is_formula(),
        lambda x: x._unpack_formula(),
        lambda x: f"'{x}' is not a formula",
    ),
    'equal': (
        lambda x: x.is_equal(),
        lambda x: x._unpack_equal(),
        lambda x: f"'{x}' is not an equation",
    ),
    'truth': (
        lambda x: x.is_truth(),
        lambda x: x._unpack_truth(),
        lambda x: f"'{x}' is not truth",
    ),
    'implies': (
        lambda x: x.is_implies(),
        lambda x: x._unpack_implies(),
        lambda x: f"'{x}' is not an implication",
    ),
    'iff': (
        lambda x: x.is_iff(),
        lambda x: x._unpack_iff(),
        lambda x: f"'{x}' is not an equivalence",
    ),
    'exists': (
        lambda x: x.is_exists(),
        lambda x: x._unpack_exists(),
        lambda x: f"'{x}' is not an existential",
    ),
    'forall': (
        lambda x: x.is_forall(),
        lambda x: x._unpack_forall(),
        lambda x: f"'{x}' is not a universal",
    )
}


for name, (f, g, h) in _assertions.items():
    a_suffix = h("")[10:]
    suffix = a_suffix[3:] if a_suffix.startswith('an ') else a_suffix[2:]

    def mk_assert_(f, h):
        def assert_(cls, arg):
            status = f(arg)
            if not status:
                raise cls.error(h(arg))
            return status
        return assert_
    assert_ = mk_assert_(f, h)
    assert_.__doc__ = f"""\
    Checks whether `arg` is {a_suffix}.

    Parameters:
       arg: Value.

    Raises:
       RuleError: `arg` is not {a_suffix}.
    """
    setattr(Rule, 'asserted_is_' + name, classmethod(assert_))

    def mk_unpack_(assert_, g):
        def unpack_(cls, arg):
            return assert_(cls, arg) and g(arg)
        return unpack_

    unpack_ = mk_unpack_(assert_, g)
    unpack_.__doc__ = f"""\
    Unpacks {suffix} `arg`.

    Parameters:
       arg: Value.

    Returns:
       `arg`'s arguments unpacked.

    Raises:
       RuleError: `arg` is not {a_suffix}.
    """
    setattr(
        Rule, 'asserted_unpack_' + name,
        classmethod(unpack_))


class PrimitiveRule(Rule):
    """Abstract base class for primitive rules."""

    def __new__(cls, *args, **kwargs):
        annotations = kwargs.pop('annotations', dict())
        seq = _Sequent(*cls._new(*args, **kwargs), **annotations)
        if cls._thy().settings.record_proofs:
            setattr(seq, '_proof', (cls, args))
        return seq

    @abstractclassmethod
    def _new(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def test(cls, arg):
        return super().test(arg)


class RuleAxiom(PrimitiveRule):
    r"""Axiom introduction.

    (Internal: Not intended for direct use.)

    Parameters:
       arg1 (:class:`Formula`): :math:`p`.
       kwargs: Annotations.

    Returns:
       :class:`Sequent`:
       :math:`⊢ p`.
    """
    @classmethod
    def _new(                   # (form,)
            cls, arg1, **kwargs):
        return set(), arg1

    @classmethod
    def _test(cls, hs, c):
        return not hs


class DerivedRule(Rule):
    """Abstract base class for derived rules."""

    def __new__(cls, *args, **kwargs):
        annotations = kwargs.pop('annotations', dict())
        return cls._new(*args, **kwargs)@annotations

    @abstractclassmethod
    def _new(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def test(cls, arg):
        return super().test(arg)
