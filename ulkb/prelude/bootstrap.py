# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import util
from ..commands import *
from ..expression import *
from ..theory import *

__all__ = [
    'TypeVariables',
    'Variables',
    'Constants',
    'BaseType',
    'BaseTypes',
    'BoolType',
    'bool_',
    'FunctionType',
    'BetaRedex',
]


def TypeVariables(              # macro: (id, ...)
        arg1, *args, **kwargs):
    """Constructs one or more :class:`TypeVariable`'s.

    Parameters:
       arg1: Id.
       args: Remaining ids.
       kwargs: Annotations.

    Returns:
       A sequence of :class:`TypeVariable`'s.
    """
    return util.map_args(
        lambda x: TypeVariable(x, **kwargs), arg1, *args)


def Variables(                  # macro: (id, ..., type)
        arg1, arg2, *args, type=None, **kwargs):
    """Constructs one or more :class:`Variable`'s.

    Parameters:
       arg1: Id.
       arg2: Id or :class:`Type`.
       args: Remaining ids.
       type: :class:`Type`.
       kwargs: Annotations.

    Returns:
       A sequence of :class:`Variable`'s.
    """
    args = [arg1, arg2, *args]
    if type is None:
        type, args = args[-1], args[:-1]
    return map(lambda x: Variable(x, type=type, **kwargs), args)


def Constants(                  # macro: (id, ..., type)
        arg1, arg2, *args, type=None, **kwargs):
    """Constructs one or more :class:`Constant`'s.

    Parameters:
       arg1: Id.
       arg2: Id or :class:`Type`.
       args: Remaining ids.
       type: :class:`Type`.
       kwargs: Annotations.

    Returns:
       A sequence of :class:`Constant`'s.
    """
    args = [arg1, arg2, *args]
    if type is None:
        type, args = args[-1], args[:-1]
    return map(lambda x: Constant(x, type=type, **kwargs), args)


class BaseType(TypeApplication):
    """Base type.

    A base type is a type obtained by applying the 0-ary constructor `arg1`.

    Parameters:
       arg1: Id.

    Returns:
       A new :class:`TypeApplication`.

    .. code-block:: python
       :caption: Example:

       t1 = BaseType('t')
       print(t1)
       # t : *

       t2 = TypeConstructor('t', 0)()
       print(t2)
       # t : *

       print(t1 == t2)
       # True

    See also:
       :func:`BaseTypes`.
    """
    def __new__(                # (id,)
            cls, arg1, **kwargs):
        return TypeConstructor(arg1, 0)(**kwargs)

    @classmethod
    def test(cls, arg):
        return TypeApplication.test(arg) and arg.head.arity == 0


def BaseTypes(                  # macro: (id, ...)
        arg1, *args, **kwargs):
    """Constructs one or more :class:`BaseType`'s.

    Parameters:
       arg1: Id.
       args: Remaining ids.
       kwargs: Annotations.

    Returns:
       A sequence of :class:`BaseType`'s.
    """
    return util.map_args(lambda x: BaseType(x, **kwargs), arg1, *args)


class BoolType(TypeApplication):
    """Bool type.

    The bool type is the type obtained by applying the 0-ary constructor
    ``'bool'``.

    It represents the type of formulas (truth-values).

    Returns:
       A new :class:`TypeApplication`.

    .. code-block:: python
       :caption: Example:

       t1 = BoolType()
       print(t1)
       # bool : *

       t2 = BaseType('bool')
       print(t2)
       # bool : *

       print(t1 == t2)
       # True

    See also:
       :class:`Formula`.
    """
    constructor = new_type_constructor('bool', 0)
    instance = None

    def __new__(                # ()
            cls, **kwargs):
        return cls.constructor(**kwargs)

    @classmethod
    def test(cls, arg):
        return arg == cls.instance

    @classmethod
    def cast(cls, arg):
        return cls.Truth() if bool(arg) else cls.Falsity()


BoolType.instance = BoolType()
bool_ = BoolType.instance
new_python_type_alias(bool, bool_, BoolType)


class FunctionType(TypeApplication):
    """Function type.

    A function type is a type obtained by applying the 2-ary constructor
    ``'fun'`` to types `arg1` and `arg2`.

    It represents the type of functions from (domain) `arg1` to (codomain)
    `arg2`.

    The 2-ary constructor ``'fun'`` is assumed to be right-associative:
    If more than two arguments are given, the result is right-folded.

    Parameters:
       arg1: :class:`Type`.
       arg2: :class:`Type`.
       args: Remaining :class:`Type`'s.
       kwargs: Annotations.

    Returns:
       A new :class:`TypeApplication`.

    .. code-block:: python
       :caption: Example:

       a, b = TypeVariables('a', 'b')
       print(FunctionType(a, b, BoolType()))
       # a → b → bool : *
    """
    constructor = new_type_constructor('fun', 2, 'right')

    def __new__(                # (type1, type2, ...)
            cls, arg1, arg2, *args, **kwargs):
        return cls.constructor(arg1, arg2, *args, **kwargs)

    @classmethod
    def test(cls, arg):
        return TypeApplication.test(arg) and arg.head == cls.constructor

    @classmethod
    def _unfold(cls, arg):
        return arg._unfold_type_application()[1:]

    @classmethod
    def _unpack(cls, arg):
        return arg._unpack_type_application()[1:]


setattr(Type, '__rshift__', lambda x, y: FunctionType(x, y))
setattr(Type, '__rrshift__', lambda x, y: FunctionType(*y, x))
setattr(Type, '__lshift__', lambda x, y: y >> x)


class BetaRedex(Application):
    """Beta-redex.

    (Internal: Not intended for direct use.)

    A beta-redex is an application of an abstraction to another term.

    Parameters:
       arg1: :class:`Abstraction`.
       arg2: :class:`Term`.
       kwargs: Annotations.

    Returns:
       A new :class:`Application`.
    """
    def __new__(                # (abs, term)
            cls, arg1, arg2, **kwargs):
        arg1 = Abstraction.check(arg1, cls.__name__, None, 1)
        return Application(arg1, arg2, **kwargs)

    @classmethod
    def test(cls, arg):
        return Application.test(arg) and arg.left.is_abstraction()
