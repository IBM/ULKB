# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import util
from ..commands import *
from ..defined import *
from ..expression import *
from ..theory import *
from .bootstrap import *

__all__ = [
    'Formula',
    'Equal',
    'Iff',
    'Truth',
    'And',
    'Implies',
    'Forall',
    'Falsity',
    'Not',
    'Or',
    'Exists',
    'Exists1',
    'equal',
    'true',
    'false',
    'not_',
    'and_',
    'or_',
    'iff',
    'implies',
    'exists',
    'exists1',
    'forall',
    'eq',
    'ne',
]


class Formula(Term):
    """Abstract base class for formulas.

    A formula is a term of type :func:`BoolType()` representing a logical
    proposition.
    """
    @classmethod
    def test(cls, arg):
        return Term.test(arg) and arg.type.is_bool_type()

    @classmethod
    def nff_prop(cls, arg):
        return cls._nnf_prop(cls._simplify_prop(arg))

    @classmethod
    def _nnf_prop(cls, arg):
        if arg.is_not():
            (p,) = arg._unpack_not()
            if p.is_not():      # ¬¬p ▷ f(p)
                (p,) = p._unpack_not()
                return cls._nnf_prop(p)
            elif p.is_and():    # ¬(p ∧ q) ▷ f(¬p) ∨ f(¬q)
                p, q = p._unpack_and()
                return Or(cls._nnf_prop(Not(p)), cls._nnf_prop(Not(q)))
            elif p.is_or():     # ¬(p ∨ q) ▷ f(¬p) ∧ f(¬q)
                p, q = p._unpack_or()
                return And(cls._nnf_prop(Not(p)), cls._nnf_prop(Not(q)))
            elif p.is_implies():  # ¬(p → q) ▷ f(p) ∧ f(¬q)
                p, q = p._unpack_implies()
                return And(cls._nnf_prop(p), cls._nnf_prop(Not(q)))
            elif p.is_iff():    # ¬(p ↔ q) ▷ (f(p) ∧ f(¬q)) ∨ (f(¬p) ∧ f(q))
                p, q = p._unpack_iff()
                return Or(
                    And(cls._nnf_prop(p), cls._nnf_prop(Not(q))),
                    And(cls._nnf_prop(Not(p)), cls._nnf_prop(q)))
        elif arg.is_and():
            p, q = arg._unpack_and()
            return And(cls._nnf_prop(p), cls._nnf_prop(q))
        elif arg.is_or():
            p, q = arg._unpack_or()
            return Or(cls._nnf_prop(p), cls._nnf_prop(q))
        elif arg.is_implies():
            p, q = arg._unpack_implies()
            return Or(cls._nnf_prop(Not(p)), cls._nnf_prop(q))
        elif arg.is_iff():
            p, q = arg._unpack_iff()
            return Or(
                And(cls._nnf_prop(p), cls._nnf_prop(q)),
                And(cls._nnf_prop(Not(p)), cls._nnf_prop(Not(q))))
        return arg

    @classmethod
    def _simplify_prop(cls, arg):
        if arg.is_not():
            (p,) = arg._unpack_not()
            arg = Not(cls._simplify_prop(p))
        elif arg.is_and():
            p, q = arg._unpack_and()
            arg = And(cls._simplify_prop(p), cls._simplify_prop(q))
        elif arg.is_or():
            p, q = arg._unpack_or()
            arg = Or(cls._simplify_prop(p), cls._simplify_prop(q))
        elif arg.is_implies():
            p, q = arg._unpack_implies()
            arg = Implies(cls._simplify_prop(p), cls._simplify_prop(q))
        elif arg.is_iff():
            p, q = arg._unpack_iff()
            arg = Iff(cls._simplify_prop(p), cls._simplify_prop(q))
        else:
            return arg
        return cls._simplify_prop1(arg)

    @classmethod
    def _simplify_prop1(cls, arg):
        if arg.is_not():
            (p,) = arg._unpack_not()
            if p.is_truth():    # ¬⊤ ▷ ⊥
                return Falsity()
            elif p.is_falsity():  # ¬⊥ ▷ ⊤
                return Truth()
            elif p.is_not():    # ¬¬q ▷ q
                (q,) = p._unpack_not()
                return q
        elif arg.is_and():
            p, q = arg._unpack_and()
            if p.is_truth():    # ⊤ ∧ q ▷ q
                return q
            elif q.is_truth():  # p ∧ ⊤ ▷ p
                return p
            elif p.is_falsity() or q.is_falsity():  # ⊥ ∧ q, p ∧ ⊥ ▷ ⊥
                return Falsity()
        elif arg.is_or():
            p, q = arg._unpack_or()
            if p.is_falsity():  # ⊥ ∨ q ▷ q
                return q
            elif q.is_falsity():  # p ∨ ⊥ ▷ p
                return p
            elif p.is_truth() or q.is_truth():  # ⊤ ∨ q, p ∨ ⊤ ▷ ⊤
                return Truth()
        elif arg.is_implies():
            p, q = arg._unpack_or()
            if p.is_truth():    # ⊤ → q ▷ q
                return q
            elif p.is_falsity() or q.is_truth():  # ⊥ → q, p → ⊤ ▷ ⊤
                return Truth()
        elif arg.is_iff():
            p, q = arg._unpack_iff()
            if p.is_truth():    # ⊤ ↔ q ▷ q
                return q
            elif q.is_truth():  # p ↔ ⊤ ▷ p
                return p
            elif p.is_falsity():  # ⊥ ↔ q ▷ ¬q
                return Not(q)
            elif q.is_falsity():  # p ↔ ⊥ ▷ ¬p
                return Not(p)
        return arg


class Equal(Application):
    r"""Equality (:math:`=`).

    Constructs an equation by applying the equality constructor
    :math:`(\mathtt{equal} : 𝛼 → 𝛼 → \mathtt{bool})` to `arg1` and `arg2`.

    Parameters:
       arg1 (:class:`Term`): :math:`t_1`.
       arg2 (:class:`Term`): :math:`t_2`.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`t_1 = t_2`.
    """
    constructor = new_constant(
        'equal', FunctionType(TypeVariable('a'), TypeVariable('a'), bool_))

    def __new__(                # (term, term)
            cls, arg1, arg2, **kwargs):
        return cls.constructor(arg1, arg2, **kwargs)

    @classmethod
    def test(cls, arg):
        return (Application.test(arg)
                and Application.test(arg.left)
                and arg.left.left.is_constant()
                and arg.left.left.id == cls.constructor.id)

    @classmethod
    def _unfold(cls, arg):
        return cls._unpack(arg)

    @classmethod
    def _unpack(cls, arg):
        (_, l), r = arg._unpack_application()
        return l, r

    @classmethod
    def eq(cls, x, y, *args, **kwargs):  # macro
        if not args:
            return cls(x, y, **kwargs)
        else:
            return And(
                *map(lambda t: cls(*t),
                     util.sliding_pairs_args(x, y, *args)), **kwargs)

    @classmethod
    def ne(cls, x, y, *args, **kwargs):  # macro
        if not args:
            return Not(cls(x, y), **kwargs)
        else:
            return And(
                *map(lambda t: Not(cls(*t)),
                     util.sliding_pairs_args(x, y, *args)), **kwargs)


class Iff(Equal):
    r"""Equivalence (bi-implication, :math:`↔`).

    Constructs a logical equivalence by applying :class:`Equal` to the
    formulas `arg1` and `arg2`.

    Equivalence is right-associative: If more than two arguments are given,
    the result is right-folded.

    Parameters:
       arg1 (:class:`Formula`): :math:`p_1`.
       arg2 (:class:`Formula`): :math:`p_2`.
       args: Remaining :class:`Formula`'s.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`p_1 ↔ (p_2 ↔ (… ↔ (p_{n-1} ↔ p_n)))`.
    """
    @classmethod
    def _constructor(cls, arg1, arg2, **kwargs):
        form1 = Formula.check(arg1, cls.__name__, None, 1)
        form2 = Formula.check(arg2, cls.__name__, None, 2)
        return Equal(form1, form2, **kwargs)

    def __new__(                # (form, form)
            cls, arg1, arg2, *args, **kwargs):
        return util.foldr_infix(
            cls._constructor, cls, arg1, arg2, *args, **kwargs)

    @classmethod
    def test(cls, arg):
        if not Equal.test(arg):
            return False
        l, r = arg._unpack_equal()
        return l.is_formula() and r.is_formula()


class Truth(
        DefinedConstant,
        definiendum='true',
        definiens=(
            lambda p:           # ()
            Equal(p >> p, p >> p))(
                Variable('p', bool_))):
    r"""Truth (:math:`⊤`).

    Constructs the true formula.

    Parameters:
       kwargs: Annotations.

    Returns:
       :class:`Constant`:
       :math:`⊤`.
    """


class And(
        DefinedInfixOperator,
        definiendum='and',
        definiens=(
            lambda p, q, f, T:     # (form, form)
            (p, q) >> Equal(f >> f(p, q), f >> f(T, T)))(
                *Variables('p', 'q', bool_),
                Variable('f', FunctionType(bool_, bool_, bool_)),
                Truth()),
        associativity='right'):
    r"""Conjunction (:math:`∧`).

    Constructs a logical conjunction by applying constructor
    :math:`(\mathtt{and} : \mathtt{bool} → \mathtt{bool} → \mathtt{bool})`
    to `arg1` and `arg2`.

    Conjunction is right-associative: If more than two arguments are given,
    the result is right-folded.

    Parameters:
       arg1 (:class:`Formula`): :math:`p_1`
       arg2 (:class:`Formula`): :math:`p_2`
       args: Remaining :class:`Formula`'s.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`p_1 ∧ (p_2 ∧ (… ∧ (p_{n-1} ∧ p_n)))`.
    """


class Implies(
        DefinedInfixOperator,
        definiendum='implies',
        definiens=(
            lambda p, q:        # (form, form)
            (p, q) >> Iff(And(p, q), p))(
                *Variables('p', 'q', bool_)),
        associativity='right'):
    r"""Implication (:math:`→`).

    Constructs a logical implication by applying constructor
    :math:`(\mathtt{implies} : \mathtt{bool} → \mathtt{bool} → \mathtt{bool})`
    to `arg1` and `arg2`.

    Implication is right-associative: If more than two arguments are given,
    the result is right-folded.

    Parameters:
       arg1 (:class:`Formula`): :math:`p_1`.
       arg2 (:class:`Formula`): :math:`p_2`.
       args: Remaining :class:`Formula`'s.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`p_1 → (p_2 → (… → (p_{n-1} → p_n)))`.
    """


class Forall(
        DefinedBinder,
        definiendum='forall',
        definiens=(
            lambda p, x, T:     # (var, form)
            p >> Equal(p, x >> T))(
                Variable('p', FunctionType(TypeVariable('a'), bool_)),
                Variable('x', TypeVariable('a')),
                Truth())):
    r"""Universal quantification (:math:`∀`).

    Constructs a universally quantified formula by applying constructor
    :math:`(\mathtt{forall} : (𝛼 → \mathtt{bool}) → \mathtt{bool})`
    to the predicate resulting from abstracting `arg1` over `arg2`.

    Universal quantification is right-associative: If more than two
    arguments are given, the result is right-folded.

    Parameters:
       arg1 (:class:`Variable`): :math:`x_1`.
       arg2 (:class:`Variable` or :class:`Formula`): :math:`p`.
       args: Remaining :class:`Variable`'s followed by a :class:`Formula`.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`∀ x_1, (∀ x_2, (…, (∀ x_{n-1}, (∀ x_n, p))))`.
    """


class Falsity(
        DefinedConstant,
        definiendum='false',
        definiens=(
            lambda p:           # ()
            Forall(p, p))(
                Variable('p', bool_))):
    r"""Falsity (:math:`⊥`).

    Constructs the false formula.

    Parameters:
       kwargs: Annotations.

    Returns:
       :class:`Constant`:
       :math:`⊥`.
    """


class Not(
        DefinedPrefixOperator,
        definiendum='not',
        definiens=(
            lambda p, F:
            p >> Implies(p, F))(
                Variable('p', bool_),
                Falsity())):
    r"""Negation (:math:`¬`).

    Constructs a logical negation by applying constructor
    :math:`(\mathtt{not} : \mathtt{bool} → \mathtt{bool})`
    to `arg1`.

    Parameters:
       arg1 (:class:`Formula`): :math:`p`
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`¬p`.
    """


class Or(
        DefinedInfixOperator,
        definiendum='or',
        definiens=(
            lambda p, q, r:     # (form, form)
            (p, q) >> Forall(r, Implies(Implies(p, r), Implies(q, r), r)))(
                *Variables('p', 'q', 'r', bool_)),
        associativity='right'):
    r"""Disjunction (:math:`∨`).

    Constructs a logical disjunction by applying constructor
    :math:`(\mathtt{or} : \mathtt{bool} → \mathtt{bool} → \mathtt{bool})` to
    `arg1` and `arg2`.

    Disjunction is right-associative: If more than two arguments are given,
    the result is right-folded.

    Parameters:
       arg1 (:class:`Formula`): :math:`p_1`
       arg2 (:class:`Formula`): :math:`p_2`
       args: Remaining :class:`Formula`'s.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`p_1 ∨ (p_2 ∨ (… ∨ (p_{n-1} ∨ p_n)))`.
    """


class Exists(
        DefinedBinder,
        definiendum='exists',
        definiens=(
            lambda p, q, x:     # (var, form)
            (p >> Forall(q, Implies((Forall(x, Implies(p(x), q))), q))))(
                Variable('p', FunctionType(TypeVariable('a'), bool_)),
                Variable('q', bool_),
                Variable('x', TypeVariable('a')))):
    r"""Existential quantification (:math:`∃`).

    Constructs an existentially quantified formula by applying constructor
    :math:`(\mathtt{exists} : (𝛼 → \mathtt{bool}) → \mathtt{bool})` to the
    predicate resulting from abstracting `arg1` over `arg2`.

    Existential quantification is right-associative: If more than two
    arguments are given, the result is right-folded.

    Parameters:
       arg1 (:class:`Variable`): :math:`x_1`.
       arg2 (:class:`Variable` or :class:`Formula`): :math:`p`.
       args: Remaining :class:`Variable`'s followed by a :class:`Formula`.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`∃ x_1, (∃ x_2, (…, (∃ x_{n-1}, (∃ x_n, p))))`.
    """


class Exists1(
        DefinedBinder,
        definiendum='exists1',
        definiens=(
            lambda p, x, y:     # (var, form)
            (p >> And(
                Exists.constructor(p),
                Forall(x, y, Implies(And(p(x), p(y)), Equal(x, y))))))(
                    Variable('p', FunctionType(TypeVariable('a'), bool_)),
                    *Variables('x', 'y', TypeVariable('a')))):
    r"""Unique existential quantification (:math:`∃!`).

    Constructs a unique existentially quantified formula by applying
    constructor
    :math:`(\mathtt{exists1} : (𝛼 → \mathtt{bool}) → \mathtt{bool})` to the
    predicate resulting from abstracting `arg1` over `arg2`.

    Unique existential quantification is right-associative: If more than two
    arguments are given, the result is right-folded.

    Parameters:
       arg1 (:class:`Variable`): :math:`x_1`.
       arg2 (:class:`Variable` or :class:`Formula`): :math:`p`.
       args: Remaining :class:`Variable`'s followed by a :class:`Formula`.
       kwargs: Annotations.

    Returns:
       :class:`Application`:
       :math:`∃! x_1, (∃! x_2, (…, (∃! x_{n-1}, (∃! x_n, p))))`.
    """


equal = Equal.constructor
true = Truth.constructor
false = Falsity.constructor
not_ = Not.constructor
and_ = And.constructor
or_ = Or.constructor
iff = Iff.constructor
implies = Implies.constructor
exists = Exists.constructor
exists1 = Exists1.constructor
forall = Forall.constructor
eq = Equal.eq
ne = Equal.ne
