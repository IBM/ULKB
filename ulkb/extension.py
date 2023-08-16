# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from . import error
from .object import Object

__all__ = [
    'Assertion',
    'Assumption',
    'Extension',
    'ExtensionError',
    'NewAxiom',
    'NewConstant',
    'NewDefinition',
    'NewPythonTypeAlias',
    'NewTheorem',
    'NewTypeConstructor',
    'NewTypeSpec',
    'Notation',
]


class ExtensionError(error.Error):
    def __init__(self, ext, reason):
        super().__init__(f'{ext.__class__.__name__}: {reason}')
        self.extension = ext
        self.reason = reason


class Extension(Object):

    @property
    def id(self):
        return self.get_id()

    def get_id(self):
        return None

    def error(self, msg):
        raise ExtensionError(self, msg)


class Assumption(Extension):
    pass


class NewTypeConstructor(Assumption):

    def __init__(self, arg1, **kwargs):
        super().__init__(       # (tcons,)
            arg1, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:              # tcons
            return self.TypeConstructor.check(
                arg, self.__class__.__name__, None, i)
        else:
            error.should_not_get_here()

    def get_id(self):
        return self[0].id


class NewConstant(Assumption):

    def __init__(               # (const,)
            self, arg1, **kwargs):
        super().__init__(arg1, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:              # const
            return self.Constant.check(
                arg, self.__class__.__name__, None, i)
        else:
            error.should_not_get_here()

    def get_id(self):
        return self[0].id


class NewAxiom(Assumption):

    def __init__(               # (const, form)
            self, arg1, arg2, **kwargs):
        super().__init__(arg1, arg2, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:              # const
            arg = self._preprocess_arg_constant(self, arg, i)
            return arg.check_formula(self.__class__.__name__, None, i)
        elif i == 2:            # form
            return self._preprocess_arg_formula(self, arg, i)
        else:
            error.should_not_get_here()

    def get_id(self):
        return self[0].id


class Assertion(Extension):
    pass


class NewDefinition(Assertion):

    def __init__(               # (equal,)
            self, arg1, **kwargs):
        super().__init__(arg1, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:              # equal
            arg = self._preprocess_arg_equal(self, arg, i)
            l, r = arg.unpack_equal()
            if not l.is_variable():
                error.arg_error(
                    arg, 'not a definitional equation',
                    self.__class__.__name__, None, i)
            elif r.has_free_variables():
                error.arg_error(
                    arg, 'definiens is not closed',
                    self.__class__.__name__, None, i)
            elif not (r.type_variables <= l.type_variables):
                msg = error._build_plural_message(
                    'extra type variable%s in definiens',
                    *(r.type_variables - l.type_variables))
                error.arg_error(
                    arg, msg, self.__class__.__name__, None, i)
            return arg
        else:
            error.should_not_get_here()

    def get_id(self):
        l, _ = self[0]._unpack_equal()
        return l.id


class NewTheorem(Assertion):

    def __init__(               # (const, seq)
            self, arg1, arg2, **kwargs):
        super().__init__(arg1, arg2, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if i == 1:              # const
            arg = self._preprocess_arg_constant(self, arg, i)
            return arg.check_formula(self.__class__.__name__, None, i)
        elif i == 2:            # seq
            return self._preprocess_arg_sequent(self, arg, i)
        else:
            error.should_not_get_here()

    def get_id(self):
        return self[0].id


class Notation(Extension):
    pass


class NewPythonTypeAlias(Notation):

    def __init__(       # (py_type, type, spec)
            self, arg1, arg2, arg3=None, **kwargs):
        super().__init__(arg1, arg2, arg3, **kwargs)

    def _preprocess_arg(self, arg, i):
        if i != 3:              # skip possible None
            arg = super()._preprocess_arg(arg, i)
        if i == 1:              # py_type or str
            arg = __builtins__.get(arg, arg)
            return error.check_arg_class(
                arg, type, self.__class__.__name__, None, i)
        elif i == 2:            # type
            return self.Type.check(
                arg, self.__class__.__name__, None, i)
        elif i == 3:
            if isinstance(arg, type):
                arg = arg.__name__
            return error.check_optional_arg(
                arg, lambda x: isinstance(x, str), None,
                None, self.__class__.__name__, None, i)
        else:
            error.should_not_get_here()


class NewTypeSpec(Notation):

    def __init__(               # (type, spec)
            self, arg1, **kwargs):
        super().__init__(arg1, **kwargs)

    def _preprocess_arg(self, arg, i):
        arg = super()._preprocess_arg(arg, i)
        if isinstance(arg, type):
            arg = arg.__name__
        return error.check_arg_class(
            arg, str, self.__class__.__name__, None, i)
