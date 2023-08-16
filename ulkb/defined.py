# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from . import util
from .commands import *
from .expression import *

__all__ = [
    'DefinedConstant',
    'DefinedPrefixOperator',
    'DefinedInfixOperator',
    'DefinedBinder',
]


class DefinedTerm(Term):

    @classmethod
    def _init_constructor(cls, definiendum, definiens):
        cls._thy().new_definition(definiendum, definiens)
        cls.constructor = lookup_constant(definiendum)
        cls.definition = lookup_definition(definiendum)
        l, r = cls.definition.conclusion.unpack_equal()
        cls.definiendum, cls.definiens = l, r

    @classmethod
    def test(cls, arg):
        return util.any_map(lambda x: x.test(arg), cls.__subclasses__())


class DefinedConstant(DefinedTerm):

    def __init_subclass__(cls, definiendum, definiens, **kwargs):
        cls._init_constructor(definiendum, definiens)

        def _mk_new():
            def _new(cls, **kwargs):
                return cls.constructor@kwargs
            return _new
        setattr(cls, '__new__', _mk_new())
        setattr(cls, 'test', classmethod(
            lambda x, arg: arg == cls.constructor))


class DefinedPrefixOperator(DefinedTerm):

    def __init_subclass__(
            cls, definiendum, definiens, precedence=None, **kwargs):
        cls._init_constructor(definiendum, definiens)

        def _mk_new():
            def _new(cls, arg1, **kwargs):
                return cls.constructor(arg1, **kwargs)
            return _new
        setattr(cls, '__new__', _mk_new())
        setattr(cls, 'test', classmethod(
            lambda x, arg: (
                Application.test(arg)
                and arg.left == x.constructor)))

    @classmethod
    def _unpack(cls, arg):
        return (arg.right,)


class DefinedInfixOperator(DefinedTerm):

    def __init_subclass__(
            cls, definiendum, definiens, associativity,
            precedence=None, **kwargs):
        cls._init_constructor(definiendum, definiens)
        cls.associativity = associativity
        cls.precedence = precedence
        _new = None
        if cls.associativity == 'left':
            def _mk_new():
                def _new(cls, arg1, arg2, *args, **kwargs):
                    return util.foldl_infix(
                        cls.constructor, cls, arg1, arg2, *args, **kwargs)
                return _new
            _new = _mk_new()
        elif cls.associativity == 'right':
            def _mk_new():
                def _new(cls, arg1, arg2, *args, **kwargs):
                    return util.foldr_infix(
                        cls.constructor, cls, arg1, arg2, *args, **kwargs)
                return _new
            _new = _mk_new()
        else:
            def _mk_new():
                def _new(cls, arg1, arg2, **kwargs):
                    return cls.constructor(arg1, arg2, **kwargs)
                return _new
            _new = _mk_new()
        setattr(cls, '__new__', _new)
        setattr(cls, 'test', classmethod(
            lambda x, arg: (
                Application.test(arg)
                and Application.test(arg.left)
                and arg.left.left == x.constructor)))

    @classmethod
    def _unfold(cls, arg):
        if hasattr(cls, 'associativity'):
            if cls.associativity == 'left':
                return tuple(util.unfoldl(cls.unpack_unsafe, arg))
            elif cls.associativity == 'right':
                return tuple(util.unfoldr(cls.unpack_unsafe, arg))
        return super()._unfold(arg)

    @classmethod
    def _unpack(cls, arg):
        (_, l), r = arg.unpack_application()
        return l, r


class DefinedBinder(DefinedTerm):

    def __init_subclass__(
            cls, definiendum, definiens, precedence=None, **kwargs):
        cls._init_constructor(definiendum, definiens)
        cls.precedence = precedence

        def _mk_new():
            def _new(cls, arg1, arg2, *args, **kwargs):
                return util.foldr_infix(
                    cls._constructor, cls, arg1, arg2, *args, **kwargs)
            return _new
        setattr(cls, '__new__', _mk_new())

        def _mk__constructor():
            def __constructor(cls, arg1, arg2, *args, **kwargs):
                x = Variable.check(arg1, cls.__name__, None, 1)
                t = Term.check(arg2, cls.__name__, None, 2)
                a = cls.constructor.type[1][1]
                c = cls.constructor.instantiate({a: x.type})
                return c(Abstraction(x, t), **kwargs)
            return __constructor
        setattr(cls, '_constructor', classmethod(_mk__constructor()))
        setattr(cls, 'test', classmethod(
            lambda x, arg: (
                Application.test(arg)
                and arg.left.is_constant()
                and arg.left.id == x.constructor.id)))

    @classmethod
    def _unfold(cls, arg):
        return tuple(util.unfoldr(cls.unpack_unsafe, arg))

    @classmethod
    def _unpack(cls, arg):
        _, t = arg.unpack_application()
        return t.unpack_abstraction()
