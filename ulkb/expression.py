# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from abc import abstractmethod

from . import error, util
from .object import Object

__all__ = [
    'Abstraction',
    'Application',
    'AtomicTerm',
    'BoundVariable',
    'CompoundTerm',
    'Constant',
    'Expression',
    'Term',
    'Type',
    'TypeApplication',
    'TypeConstructor',
    'TypeVariable',
    'Variable',
]


class Expression(Object):
    """Abstract base class for expressions.

    An :class:`Expression` can be either a :class:`Type` or a :class:`Term`.

    Parameters:
       args: Arguments
       kwargs: Annotations.

    Returns:
       :class:`Expression`.
    """
    __slots__ = (
        '_cached_unfolded_args',
        '_cached_type_constructors',
        '_cached_type_variables',
    )

    def __neg__(self):          # FIXME: generalize
        return self.Not(self)

    def __invert__(self):       # FIXME: generalize
        return self.Not(self)

    def __and__(self, other):   # FIXME: generalize
        return self.And(self, other)

    def __rand__(self, other):  # FIXME: generalize
        return self.And(other, self)

    def __or__(self, other):    # FIXME: generalize
        return self.Or(self, other)

    def __ror__(self, other):   # FIXME: generalize
        return self.Or(other, self)

    def _build_unfolded_args_cache(self):
        """Gets the expression arguments unfolded."""
        return tuple(self._get_unfolded_args_iterator())

    def _get_unfolded_args_iterator(self):  # defaults to args
        return iter(self.args)

    def has_type_constructors(self):
        """Tests whether some type constructor occurs in expression.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return bool(self.type_constructors)

    def _build_type_constructors_cache(self):
        """Gets the set of type constructors occurring in expression."""
        return frozenset(self._get_type_constructors_iterator())

    @abstractmethod
    def _get_type_constructors_iterator(self):
        raise NotImplementedError

    def has_type_variables(self):
        """Tests whether some type variable occurs in expression.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return bool(self.type_variables)

    def _build_type_variables_cache(self):
        """Gets the set of type variables occurring in expression."""
        return frozenset(self._get_type_variables_iterator())

    @abstractmethod
    def _get_type_variables_iterator(self):
        raise NotImplementedError

    def instantiate(self, theta):
        """Applies type-variable instantiation `theta` to expression.

        Parameters:
           theta: Dictionary mapping type variables to types.

        Returns:
           The resulting :class:`Expression`.

        .. code-block:: python
           :caption: Example:

           a, b = TypeVariables('a', 'b')
           f = Constant('f', FunctionType(a, b))
           x = Variable('x', a)

           print(f(x))
           # (f : a → b) (x : a)

           print(f(x).instantiate({a: BaseType('nat'), b: BoolType()}))
           # (f : nat → bool) (x : nat)
        """
        return self._instantiate(theta)[0] if theta else self

    @abstractmethod
    def _instantiate(self, theta):
        raise NotImplementedError


class TypeConstructor(Expression):
    """Type constructor.

    Type constructors are the building blocks of type expressions.

    Parameters:
       arg1: Id.
       arg2: Arity.
       arg3: Associativity (``'left'`` or ``'right'``).
       kwargs: Annotations.

    Returns:
       A new :class:`TypeConstructor`.
    """
    _associativity_values = {'left', 'right'}

    def __init__(               # (id, arity, associativity)
            self, arg1, arg2, arg3=None, **kwargs):
        super().__init__(arg1, arg2, arg3, **kwargs)

    def _preprocess_arg(self, arg, i):
        if i != 3:              # skip possible None
            arg = super()._preprocess_arg(arg, i)
        if i == 1:
            return self._preprocess_arg_id(self, arg, i)
        elif i == 2:
            return abs(error.check_arg_class(
                arg, int, self.__class__.__name__, None, i))
        elif i == 3:
            return error.check_optional_arg_enum(
                arg, self._associativity_values, None,
                self.__class__.__name__, None, i)
        else:
            error.should_not_get_here()

    def __call__(self, *args, **kwargs):
        if self.associativity is None or len(args) <= self.arity:
            return TypeApplication(self, *args, **kwargs)
        elif self.associativity == 'left':
            return util.foldl1(
                lambda x, y: TypeApplication(self, x, y),
                args).with_annotations(**kwargs)
        elif self.associativity == 'right':
            return util.foldr1(
                lambda x, y: TypeApplication(self, x, y),
                args).with_annotations(**kwargs)
        else:
            error.should_not_get_here()

    @property
    def id(self):
        """Type constructor id."""
        return self.get_id()

    def get_id(self):
        """Gets type constructor id.

        Returns:
           Type constructor id.
        """
        return self[0]

    @property
    def arity(self):
        """Type constructor arity."""
        return self.get_arity()

    def get_arity(self):
        """Gets type constructor arity.

        Returns:
           Type constructor arity.
        """
        return self[1]

    @property
    def associativity(self):
        """Type constructor associativity."""
        return self.get_associativity()

    def get_associativity(self):
        """Gets type constructor associativity.

        Returns:
           Type constructor associativity.
        """
        return self[2]

    def _get_type_constructors_iterator(self):  # Expression
        return iter([self])

    def _get_type_variables_iterator(self):  # Expression
        return iter(())

    def _instantiate(self, theta):  # Expression
        return self, False


class Type(Expression):
    """Abstract base class for types.

    A type is an expression representing a structured collection of values.

    It can be either a :class:`TypeVariable` or a :class:`TypeApplication`.
    """

    @staticmethod
    def _preprocess_arg_type(self, arg, i):
        if isinstance(arg, type):
            try:
                return self._thy().lookup_python_type_alias(arg)
            except LookupError as err:
                return error.arg_error(
                    arg, err, self.__class__.__name__, None, i)
        else:
            return Type.check(arg, self.__class__.__name__, None, i)

    def match(self, other, theta=None):
        """Finds an instantiation that makes type match `other`.

        Parameters:
           other: :class:`Type`.
           theta: Dictionary mapping variables to types.

        Returns:
           A type-variable instantiation (theta) if successful;
           ``None`` otherwise.

        .. code-block:: python
           :caption: Example:

           a, b = TypeVariables('a', 'b')
           t1 = FunctionType(a, b)
           t2 = FunctionType(bool, bool, bool)

           print(t1.match(t2))
           # {(a : *): (bool : *), (b : *): (bool → bool : *)}
        """
        other = Type.check(other, 'match', 'other', 1)
        return self._match(other, theta or dict())

    def matches(self, other):
        """Tests whether type can instantiated to match `other`.

        Parameters:
           other: :class:`Type`.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return self.match(other) is not None

    @abstractmethod
    def _match(self, other, theta):
        raise NotImplementedError


class TypeVariable(Type):
    """Type variable.

    A type variable is an expression representing an arbitrary type.

    Parameters:
       arg1: Id.
       kwargs: Annotations.

    Returns:
       A new :class:`TypeVariable`.

    .. code-block:: python
       :caption: Example:

       a = TypeVariable('a')
       print(a)
       # a : *

    See also:
       :func:`TypeVariables`.
    """

    def __init__(               # (id,)
            self, arg1, **kwargs):
        super().__init__(arg1, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:
            return self._preprocess_arg_id(self, arg, i)
        else:
            error.should_not_get_here()

    @property
    def id(self):
        """Type variable id."""
        return self.get_id()

    def get_id(self):
        """Gets type variable id.

        Returns:
           Type variable id.
        """
        return self[0]

    def _get_type_constructors_iterator(self):  # Expression
        return iter(())

    def _get_type_variables_iterator(self):  # Expression
        return iter([self])

    def _instantiate(self, theta):  # Expression
        if self in theta:
            return theta[self], True
        else:
            return self, False

    def _match(self, other, theta):  # Type
        if self in theta:
            return theta if theta[self] == other else None
        else:
            theta[self] = other
            return theta


class TypeApplication(Type):
    """Type application.

    A type application is an expression representing the type obtained by
    the application of a type constructor to other types.

    Parameters:
       arg1: :class:`TypeConstructor`.
       args: :class:`Type`'s.
       kwargs: Annotations.

    Returns:
       A new :class:`TypeApplication`.

    .. code-block:: python
       :caption: Example:

       c0 = TypeConstructor('c0', 0)
       print(c0())              # Equivalent to: TypeApplication(c0)
       # c0 : *

       c1 = TypeConstructor('c1', 1)
       print(c1(c0()))          # Equivalent to: TypeApplication(c1, c0())
       # c1 c0 : *
    """

    @classmethod
    def _unfold(cls, arg):
        tcons = arg.head
        if tcons.arity == 2:
            l, r = arg.tail
            if tcons.associativity == 'left':
                return tcons, *util.unfoldl(lambda x: x.tail if (
                    x.is_type_application()
                    and x.head == tcons) else None, arg)
            elif tcons.associativity == 'right':
                return tcons, *util.unfoldr(lambda x: x.tail if (
                    x.is_type_application()
                    and x.head == tcons) else None, arg)
        return super()._unfold(arg)

    def __init__(               # (tcons, type, ..., type)
            self, arg1, *args, **kwargs):
        super().__init__(arg1, *args, **kwargs)

    def _preprocess_args(self, args):
        args = super()._preprocess_args(args)
        tcons, exp, got = args[0], args[0].arity, len(args) - 1
        if exp != got:
            qtd = 'few' if got < exp else 'many'
            error.arg_error(
                tcons,
                f'too {qtd} arguments: expected {exp}, got {got}',
                self.__class__.__name__, None, 1)
        return args

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:
            return self._preprocess_arg_type_constructor(self, arg, i)
        else:
            return self._preprocess_arg_type(self, arg, i)

    @property
    def head(self):
        """Type application head.

        .. code-block:: python
           :caption: Example:

           c0 = TypeConstructor('c0', 0)
           c1 = TypeConstructor('c1', 1)
           c2 = TypeConstructor('c2', 2)
           print(c2(c1(c0()), c0()).head)
           # c2
        """
        return self.get_head()

    def get_head(self):
        """Gets type application head.

        Returns:
           Type application head.
        """
        return self[0]

    @property
    def tail(self):
        """Type application tail.

        .. code-block:: python
           :caption: Example:

           c0 = TypeConstructor('c0', 0)
           c1 = TypeConstructor('c1', 1)
           c2 = TypeConstructor('c2', 2)
           print(c2(c1(c0()), c0()).head)
           # (c1 c0 : *, c0 : *)
        """
        return self.get_tail()

    def get_tail(self):
        """Gets type application tail.

        Returns:
           Type application tail.
        """
        return self[1:]

    def _get_unfolded_args_iterator(self):  # Expression
        return iter(self._unfold_type_application())

    def _get_type_constructors_iterator(self):  # Expression
        return util.chain(
            [self.head],
            *map(lambda x: x.get_type_constructors(), self.tail))

    def _get_type_variables_iterator(self):  # Expression
        return util.chain(
            *map(lambda x: x.get_type_variables(), self.tail))

    def _instantiate(self, theta):  # Expression
        args, status = [self.head], False
        for x in self.tail:
            y, s = x._instantiate(theta)
            args.append(y)
            status |= s
        return self.with_args(*args), status

    def _match(self, other, theta):  # Type
        if not other.is_type_application():
            return None
        h1, *t1 = self._unpack_type_application()
        h2, *t2 = other._unpack_type_application()
        if h1 != h2 or len(t1) != len(t2):
            return None
        for a, b in zip(t1, t2):
            theta = a.match(b, theta)
            if theta is None:
                return None
        return theta


class Term(Expression):
    """Abstract base class for terms.

    A term is an expression representing a value of a type.

    It can be either a :class:`Variable`, :class:`Constant`,
    :class:`Application`, or :class:`Abstraction`.
    """
    __slots__ = (
        '_cached_type',
        '_cached_constants',
        '_cached_variables',
        '_cached_bound_variables',
        '_cached_free_variables',
        '_cached_nameless_variables',
    )

    @staticmethod
    def _preprocess_arg_term(self, arg, i):
        if not Term.test(arg):
            try:
                spec = self._thy().lookup_python_type_alias_spec(type(arg))
                if hasattr(spec, 'cast'):
                    arg = spec.cast(arg)
            except LookupError:
                pass
        return Term.check(arg, self.__class__.__name__, None, i)

    def __call__(self, *args, **kwargs):
        if (not args and self.is_atomic_term()
                and not self.type.is_function_type()):
            return self.with_annotations(**kwargs)
        else:
            return Application(self, *args, **kwargs)

    def __rshift__(self, other):
        return Abstraction(self, other)

    def __rrshift__(self, other):
        return Abstraction(*other, self)

    def __lshift__(self, other):
        return other >> self

    def _build_type_cache(self):
        """Gets the term type."""
        return self._get_type()

    @abstractmethod
    def _get_type(self):
        raise NotImplementedError

    def has_constants(self):
        """Tests whether some constant occurs in term.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return bool(self.constants)

    def _build_constants_cache(self):
        """Gets the set of constants occurring in term."""
        return frozenset(self._get_constants_iterator())

    @abstractmethod
    def _get_constants_iterator(self):
        raise NotImplementedError

    def has_occurrence_of(self, x):
        """Tests whether variable `x` occurs (bound or free) in term.

        Parameters:
           x: :class:`Variable`.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return x in self.variables

    def has_variables(self):
        """Tests whether some variable occurs in term.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return bool(self.variables)

    def _build_variables_cache(self):
        """Gets the set of variables occurring in term."""
        return frozenset(self._get_variables_iterator())

    @abstractmethod
    def _get_variables_iterator(self):
        raise NotImplementedError

    def has_bound_occurrence_of(self, x):
        """Tests whether variable `x` occurs bound in term.

        Parameters:
           x: :class:`Variable`.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return x in self.bound_variables

    def has_bound_variables(self):
        """Tests whether some bound variable occurs in term.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return bool(self.bound_variables)

    def _build_bound_variables_cache(self):
        """Gets the set of bound variables occurring in term."""
        return frozenset(self._get_bound_variables_iterator())

    @abstractmethod
    def _get_bound_variables_iterator(self):
        raise NotImplementedError

    def has_free_occurrence_of(self, x):
        """Tests whether variable `x` occurs free in term.

        Parameters:
           x: :class:`Variable`.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return x in self.free_variables

    def has_free_variables(self):
        """Tests whether some free variable occurs in term.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return bool(self.free_variables)

    def _build_free_variables_cache(self):
        """Gets the set of free variables occurring in term."""
        return frozenset(self._get_free_variables_iterator())

    @abstractmethod
    def _get_free_variables_iterator(self):
        raise NotImplementedError

    def has_nameless_occurrence_of(self, x):
        """Tests whether nameless variable `x` occurs in term.

        Parameters:
           x: :class:`BoundVariable`.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return x in self.nameless_variables

    def has_nameless_variables(self):
        """Tests whether some nameless variable occurs in term.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return bool(self.nameless_variables)

    def _build_nameless_variables_cache(self):
        """Gets the set of nameless variables occurring in term."""
        return frozenset(self._get_nameless_variables_iterator())

    @abstractmethod
    def _get_nameless_variables_iterator(self):
        raise NotImplementedError

    def open(self, x):
        """Replaces free variable `x` by bound variable in term.

        (Internal: Not intended for direct use.)

        Parameters:
           x: :class:`Variable`.

        Returns:
           A new :class:`Term`.

        .. code-block:: python
           :caption: Example:

           x, y = Variables('x', 'y', BoolType())
           t = Abstraction(x, y)(y)
           print(t.open(y))
           # (𝜆 (x : bool) ⇒ (1 : bool)) (0 : bool)

        See also:
           :class:`BoundVariable`, :func:`Term.close`.
        """
        return self._open(x, 0)

    @abstractmethod
    def _open(self, x, i):
        raise NotImplementedError

    def close(self, term):
        """Replaces bound variable by `term` in term.

        (Internal: Not intended for direct use.)

        Parameter:
           term: :class:`Term`.

        Returns:
           A new :class:`Term`.

        .. code-block:: python
           :caption: Example:

           x, y, z = Variables('x', 'y', 'z', BoolType())
           t = Abstraction(x, y)(y)
           t1 = t.open(y)
           print(t1)
           # (𝜆 (x : bool) ⇒ (1 : bool)) (0 : bool)

           t2 = t1.close(z)
           print(t2)
           # (𝜆 (x : bool) ⇒ (z : bool)) (z : bool)

        See also:
           :class:`BoundVariable`, :func:`Term.open`.
        """
        return self._close(term, 0)

    @abstractmethod
    def _close(self, term, i):
        raise NotImplementedError

    def substitute(self, theta):
        """Applies free-variable substitution `theta` to term.

        Parameters:
           theta: Dictionary mapping variables to terms.

        Returns:
           The resulting :class:`Term`.

        Raises:
           ValueError: `theta` is invalid.

        .. code-block:: python
           :caption: Example:

           a = TypeVariable('a')
           x, y, z = Variables('x', 'y', 'z', a)
           f = Constant('f', FunctionType(a, a, a))

           t = Abstraction(x, f(x, y))
           print(t.substitute({y: z}))
           # 𝜆 x ⇒ f x z

           t = Abstraction(x, f(x, y))
           print(t.substitute({y: x}))
           # 𝜆 x0 ⇒ f x0 x
        """
        for v, t in theta.items():
            if not Variable.test(v) or not Term.test(t) or v.type != t.type:
                return error.arg_error(
                    theta, 'invalid theta', 'substitute', 'theta', 1)
        return self._substitute(theta)[0] if theta else self

    @abstractmethod
    def _substitute(self, theta):
        raise NotImplementedError


class AtomicTerm(Term):
    """Abstract base class for atomic terms."""

    @abstractmethod
    def __init__(               # (id, type)
            self, arg1, type=None, **kwargs):
        super().__init__(arg1, type, **kwargs)

    def _preprocess_arg(self, arg, i):
        if i == 1:
            return self._preprocess_arg_id(self, arg, i)
        elif i == 2:
            return self._preprocess_arg_type(self, arg, i)
        else:
            error.should_not_get_here()

    def __matmul__(self, kwargs):
        if isinstance(kwargs, dict):
            return super().__matmul__(kwargs)
        else:
            return self.with_type(
                self._preprocess_arg_type(self, kwargs, 2))

    @property
    def id(self):
        """Atomic term id."""
        return self.get_id()

    def get_id(self):
        """Get atomic term id.

        Returns:
           Atomic term id.
        """
        return self[0]

    def _get_type_constructors_iterator(self):  # Expression
        return self.type.get_type_constructors()

    def _get_type_variables_iterator(self):  # Expression
        return self.type.get_type_variables()

    def _instantiate(self, theta):  # Expression
        type, status = self.type._instantiate(theta)
        if status:
            return self.with_type(type), True
        else:
            return self, False

    def _get_type(self):        # Term
        return self[1]

    def with_type(self, type):
        """Copies atomic term overwriting its type.

        Parameters:
           type: :class:`Type`.

        Returns:
           The resulting :class:`AtomicTerm`.

        .. code-block:: python
           :caption: Equivalent to:

           term.copy(term.id, type)
        """
        return self.with_args(self.id, type)


class Variable(AtomicTerm):
    """Variable.

    A variable is an atomic expression representing an arbitrary
    value of a type.

    Parameters:
       arg1: Id.
       type: :class:`Type`.
       kwargs: Annotations.

    Returns:
       A new :class:`Variable`.

    See also:
       :func:`Variables`.
    """

    def __init__(               # (id, type)
            self, arg1, type=None, **kwargs):
        super().__init__(arg1, type=type, **kwargs)

    def _get_constants_iterator(self):  # Term
        return iter(())

    def _get_variables_iterator(self):  # Term
        return iter([self])

    def _get_bound_variables_iterator(self):  # Term
        return iter(())

    def _get_free_variables_iterator(self):  # Term
        return iter([self])

    def _get_nameless_variables_iterator(self):  # Term
        return iter(())

    def _open(self, x, i):      # Term
        if self.id == x.id and self.type == x.type:
            return BoundVariable(i, self.type)
        else:
            return self

    def _close(self, term, i):  # Term
        return self

    def _substitute(self, theta):  # Term
        if self in theta:
            return theta[self], True
        else:
            return self, False

    def occurs_in(self, it):
        """Tests whether variable occurs in some term in `it`.

        Parameters:
           it: Iterable.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return util.any_map(lambda x: x.has_occurrence_of(self), iter(it))

    def occurs_bound_in(self, it):
        """Tests whether variable occurs bound in some term in `it`.

        Parameters:
           it: Iterable.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return util.any_map(
            lambda x: x.has_bound_occurrence_of(self), iter(it))

    def occurs_free_in(self, it):
        """Tests whether variable occurs free in some term in `it`.

        Parameters:
           it: Iterable.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return util.any_map(
            lambda x: x.has_free_occurrence_of(self), iter(it))

    def get_variant(self, avoid_test):
        """Gets a variant that passes `avoid_test`.

        `avoid_test` is a function that takes a variable and returns
        ``True`` if it is unacceptable, or ``False`` if it is acceptable.

        If variable passes `avoid_test`, returns variable itself.
        Otherwise, generates and returns a similarly named variant that
        passes `avoid_test`.

        Parameter:
           avoid_test: Function.

        Returns:
           Variable itself or a new similarly named variant.

        .. code-block:: python
           :caption: Example:

           x = Variable('x', BoolType())

           print(x.get_variant(lambda v: v == x))
           # x : bool

           print(x.get_variant(lambda v: v.id in {'x', 'x0', 'x1'}))
           # x2 : bool
        """
        x = self
        while avoid_test(x):
            x = x.with_args(util.get_variant(x.id), x.type)
        return x

    def get_variant_not_in(self, avoid):
        """Gets a variant that does not occur in `avoid`.

        If variable does not occur in `avoid`, returns variable itself.
        Otherwise, generates and returns a similarly named variant that does
        not occur in `avoid`.

        Parameters:
           avoid: Iterable.

        Returns:
           Variable itself or a similarly named variant.

        See also:
           :func:`Variable.get_variable`.
        """
        return self.get_variant(lambda x: x.occurs_in(avoid))

    def get_variant_not_bound_in(self, avoid):
        """Gets a variant that does not occur bound in `avoid`.

        If variable does not occur bound in `avoid`, returns variable
        itself.  Otherwise, generates and returns a similarly named variant
        that does not occur bound in `avoid`.

        Parameters:
           avoid: Iterable.

        Returns:
           Variable itself or a similarly named variant.

        See also:
           :func:`Variable.get_variable`.
        """
        return self.get_variant(lambda x: x.occurs_bound_in(avoid))

    def get_variant_not_free_in(self, avoid):
        """Gets a variant that does not occur free in `avoid`.

        If variable does not occur free in `avoid`, returns variable itself.
        Otherwise, generates and returns a similarly named variant that does
        not occur free in `avoid`.

        Parameters:
           avoid: Iterable.

        Returns:
           Variable itself or a similarly named variant.

        See also:
           :func:`Variable.get_variable`.
        """
        return self.get_variant(lambda x: x.occurs_free_in(avoid))


class BoundVariable(Variable):
    """Bound variable.

    (Internal: Not intended for direct use.)

    Internally, terms use what is called a `locally nameless representation`.
    This is a combination of using De Bruijn indices for variables local to
    the current term (:class:`BoundVariable`) and names for variables global
    to the current term (:class:`Variable`).  See C. McBride and J. McKinna,
    "Functional Pearl: I am not a number--I am a free variable", Haskell'04,
    2004. ACM.

    See also:
       :func:`Term.open`, :func:`Term.close`.
    """

    def __init__(               # (id, type)
            self, arg1, type=None, **kwargs):
        super().__init__(arg1, type=type, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:
            return error.check_arg_class(
                arg, int, self.__class__.__name__, None, i)
        elif i == 2:
            return arg
        else:
            error.should_not_get_here()

    def _get_constants_iterator(self):  # Term
        return iter(())

    def _get_variables_iterator(self):  # Term
        return iter(())

    def _get_bound_variables_iterator(self):  # Term
        return iter(())

    def _get_free_variables_iterator(self):  # Term
        return iter(())

    def _get_nameless_variables_iterator(self):  # Term
        return iter([self])

    def _open(self, x, i):      # Term
        return self

    def _close(self, term, i):  # Term
        if self.id == i and self.type == term.type:
            return term
        else:
            return self

    def _substitute(self, theta):  # Term
        return self, False

    def occurs_in(self, it):    # Variable
        error.should_not_get_here()

    def occurs_bound_in(self, it):  # Variable
        error.should_not_get_here()

    def occurs_free_in(self, it):  # Variable
        error.should_not_get_here()

    def get_variant(self, avoid_test):  # Variable
        error.should_not_get_here()

    def get_variant_not_in(self, avoid):  # Variable
        error.should_not_get_here()

    def get_variant_not_bound_in(self, avoid):  # Variable
        error.should_not_get_here()

    def get_variant_not_free_in(self, avoid):  # Variable
        error.should_not_get_here()


class Constant(AtomicTerm):
    """Constant.

    A constant is an atomic expression representing a particular
    value of a type.

    Parameters:
       arg1: Id.
       type: :class:`Type`.
       kwargs: Annotations.

    Returns:
       A new :class:`Constant`.

    See also:
       :func:`Constants`.
    """

    def __init__(               # (id, type)
            self, arg1, type=None, **kwargs):
        super().__init__(arg1, type=type, **kwargs)

    def _get_constants_iterator(self):  # Term
        return iter([self])

    def _get_variables_iterator(self):  # Term
        return iter(())

    def _get_bound_variables_iterator(self):  # Term
        return iter(())

    def _get_free_variables_iterator(self):  # Term
        return iter(())

    def _get_nameless_variables_iterator(self):  # Term
        return iter(())

    def _open(self, x, i):      # Term
        return self

    def _close(self, term, i):  # Term
        return self

    def _substitute(self, theta):  # Term
        return self, False


class CompoundTerm(Term):
    """Abstract base class for compound terms."""

    @property
    def left(self):
        """First argument of compound term."""
        return self.get_left()

    def get_left(self):
        """Gets the first argument of compound term.

        Returns:
           First argument of compound term.
        """
        return self[0]

    @property
    def right(self):
        """Second argument of compound term."""
        return self.get_right()

    def get_right(self):
        """Gets the second argument of compound term.

        Returns:
           Second argument of compound term."""
        return self[1]

    def _get_type_variables_iterator(self):  # Expression
        return util.chain(
            self[0].get_type_variables(),
            self[1].get_type_variables())


class Application(CompoundTerm):
    """Application.

    An application is a compound expression representing the application
    of `arg1` to `arg2`.

    Application is left-associative: If more than two arguments are given,
    the result is left-folded.

    Parameters:
       arg1: :class:`Term`.
       arg2: :class:`Term`.
       args: Remaining :class:`Term`'s.
       kwargs: Annotations.

    Returns:
       A new :class:`Application`.

    Raises:
       ValueError: `arg1` cannot be applied to `arg2`.
    """

    @classmethod
    def _unfold(cls, arg):
        return tuple(util.unfoldl(
            Application.unpack_application_unsafe, arg))

    def __init__(               # (term1, term2, ...)
            self, arg1, arg2, *args, **kwargs):
        util.foldl_infix(
            super().__init__, self.__class__, arg1, arg2, *args, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        arg = self._preprocess_arg_term(self, arg, i)
        if i == 1:
            return error.check_arg(
                arg, arg.type.test_function_type(), 'not a function',
                self.__class__.__name__, None, i)
        elif i == 2:
            return arg
        else:
            error.should_not_get_here()

    def _preprocess_args(self, args):
        args = super()._preprocess_args(args)
        dom, _ = args[0].type.unpack_function_type()
        got = args[1].type
        theta = dom.match(got)
        if theta is None:
            error.arg_error(
                args[1], f"expected '{dom}', got '{got}'",
                self.__class__.__name__, None, 1)
        elif theta:
            return args[0].instantiate(theta), args[1]
        return args

    def _get_unfolded_args_iterator(self):  # Expression
        return iter(self._unfold_application())

    def _get_type_constructors_iterator(self):  # Expression
        return util.chain(
            self[0].get_type_constructors(),
            self[1].get_type_constructors())

    def _instantiate(self, theta):  # Expression
        left, lstatus = self[0]._instantiate(theta)
        right, rstatus = self[1]._instantiate(theta)
        if lstatus or rstatus:
            return self.with_args(left, right), True
        else:
            return self, False

    def _get_type(self):        # Term
        return self[0].type[2]

    def _get_constants_iterator(self):  # Term
        return util.chain(
            self[0].get_constants(),
            self[1].get_constants())

    def _get_variables_iterator(self):  # Term
        return util.chain(
            self[0].get_variables(),
            self[1].get_variables())

    def _get_bound_variables_iterator(self):  # Term
        return util.chain(
            self[0].get_bound_variables(),
            self[1].get_bound_variables())

    def _get_free_variables_iterator(self):  # Term
        return util.chain(
            self[0].get_free_variables(),
            self[1].get_free_variables())

    def _get_nameless_variables_iterator(self):  # Term
        return util.chain(
            self[0].get_nameless_variables(),
            self[1].get_nameless_variables())

    def _open(self, x, i):      # Term
        freel = self[0].has_free_occurrence_of(x)
        freer = self[1].has_free_occurrence_of(x)
        if freel and freer:
            return self.with_args(
                self[0]._open(x, i), self[1]._open(x, i))
        elif freel:
            return self.with_args(self[0]._open(x, i), self[1])
        elif freer:
            return self.with_args(self[0], self[1]._open(x, i))
        else:
            return self

    def _close(self, term, i, _nty=Term.get_type):  # Term
        lessl = term.type in map(_nty, self[0].nameless_variables)
        lessr = term.type in map(_nty, self[1].nameless_variables)
        if lessl and lessr:
            return self.with_args(
                self[0]._close(term, i), self[1]._close(term, i))
        elif lessl:
            return self.with_args(self[0]._close(term, i), self[1])
        elif lessr:
            return self.with_args(self[0], self[1]._close(term, i))
        else:
            return self

    def _substitute(self, theta):  # Term
        left, lstatus = self[0]._substitute(theta)
        right, rstatus = self[1]._substitute(theta)
        if lstatus or rstatus:
            return self.with_args(left, right), True
        else:
            return self, False


class Abstraction(CompoundTerm):
    """Abstraction.

    An abstraction is a compound expression representing the function
    obtained by abstracting variable `arg1` over `arg2`.

    Abstraction is right-associative: If more than two arguments are given,
    the result is right-folded.

    Parameters:
       arg1: :class:`Variable`.
       arg2: :class:`Variable` or :class:`Term`.
       args: Remaining :class:`Variable`'s followed by a :class:`Term`.
       _open: Whether to open `arg1` in `arg2`.
          (Internal: Not intended for direct use.)
       kwargs: Annotations.

    Returns:
       A new :class:`Abstraction`.
    """

    @classmethod
    def _dup(cls, *args, **kwargs):
        return cls(*args, _open=False, **kwargs)

    @classmethod
    def _unfold(cls, arg):
        return tuple(util.unfoldr(
            Abstraction.unpack_abstraction_unsafe, arg))

    @classmethod
    def _unpack(cls, arg):
        return arg.left, arg.right

    __slots__ = (
        '_cached_undebruijned_args',
    )

    def __init__(               # (var1, var2, ..., term)
            self, arg1, arg2, *args, _open=True, **kwargs):
        self._open_flag = _open  # hack to pass _open to _preprocess_args;
        if not args:             # we can't use util.foldr_infix below
            super().__init__(arg1, arg2, **kwargs)
        else:
            arg2 = self.__class__(arg2, *args, _open=_open)
            return super().__init__(arg1, arg2, **kwargs)

    def __eq__(self, other):    # anonymize arg[0]
        return (type(self) == type(other)
                and self[0].type == other[0].type
                and self[1] == other[1])

    def __hash__(self):         # anonymize arg[0]
        return hash((self.__class__, self[0].type, self[1]))

    def _dump(self):            # anonymize arg[0]
        cls_name = self.__class__.__name__
        return f'({cls_name} {self[0].type.dump()} {self[1].dump()})'

    def _preprocess_arg(self, arg, i, **kwargs):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:
            return self._preprocess_arg_variable(self, arg, i)
        elif i == 2:
            return self._preprocess_arg_term(self, arg, i)
        else:
            error.should_not_get_here()

    def _preprocess_args(self, args):
        args = super()._preprocess_args(args)
        open_flag = self._open_flag
        delattr(self, '_open_flag')
        if open_flag:
            return args[0], args[1].open(args[0])
        else:
            return args

    def _get_unfolded_args_iterator(self):  # Expression
        return iter(self._unfold_abstraction())

    def _get_type_constructors_iterator(self):  # Expression
        return util.chain(
            [self.type.head],
            self[0].get_type_constructors(),
            self[1].get_type_constructors())

    def _instantiate(self, theta):  # Expression
        left, lstatus = self[0]._instantiate(theta)
        right, rstatus = self[1]._instantiate(theta)
        if not lstatus and not rstatus:
            return self, False
        if left.occurs_free_in([right]):
            left = left.get_variant_not_free_in([right])
        return self.with_args(left, right), True

    def _get_type(self):        # Term
        return self.FunctionType(self[0].type, self[1].type)

    def _get_constants_iterator(self):  # Term
        return iter(self[1].get_constants())

    def _get_variables_iterator(self):  # Term
        return util.chain([self[0]], self[1].get_variables())

    def _get_bound_variables_iterator(self):  # Term
        return util.chain([self[0]], self[1].get_bound_variables())

    def _get_free_variables_iterator(self):  # Term
        return iter(self[1].get_free_variables())

    def _get_nameless_variables_iterator(self):  # Term
        return iter(self[1].get_nameless_variables())

    def _open(self, x, i):      # Term
        if not self[1].has_free_occurrence_of(x):
            return self
        else:
            return self.with_args(self[0], self[1]._open(x, i + 1))

    def _close(self, term, i, _nty=Term.get_type):  # Term
        if term.type not in map(_nty, self[1].nameless_variables):
            return self
        else:
            return self.with_args(self[0], self[1]._close(term, i + 1))

    def _substitute(self, theta):
        left = self[0]
        right, rstatus = self[1]._substitute(theta)
        if not rstatus:
            return self, False
        if left.occurs_in([right]):  # rename
            left = left.get_variant_not_in([right])
        return self.with_args(left, right), True

    def get_right(self):        # CompoundTerm
        return self.undebruijned_args[1]

    def _build_undebruijned_args_cache(self):
        """Gets the arguments of abstraction un-De Bruijn'ed."""
        return self[0], self[1].close(self[0])

    def rename(self, x):
        """Renames bound variable to `x`.

        If `x` occurs free in the abstraction, instead of `x` uses its first
        variant not free in the abstraction.

        Parameters:
           x: :class:`Variable`.

        Returns:
           A new :class:`Abstraction`.

        See also:
           :func:`Variable.get_variant_not_free_in`.

        """
        if x == self[0]:
            return self
        else:
            if x.occurs_in([self[1]]):
                x = x.get_variant_not_in([self[1]])
            return self.with_args(x, self[1])
