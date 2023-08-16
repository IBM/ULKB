# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from . import util

__all__ = [
    'EmptyTheory',
    '_thy',
    'enumerate_extensions',
    'extend',
    'lookup_axiom',
    'lookup_constant',
    'lookup_definition',
    'lookup_extension',
    'lookup_python_type_alias',
    'lookup_theorem',
    'lookup_type_constructor',
    'new_axiom',
    'new_base_type',
    'new_constant',
    'new_definition',
    'new_python_type_alias',
    'new_theorem',
    'new_type_constructor',
    'reset',
    'settings',
    'show_axioms',
    'show_constants',
    'show_definitions',
    'show_extensions',
    'show_python_type_aliases',
    'show_theorems',
    'show_type_constructors',
]


def _thy(theory=None):
    """Gets `theory` or the top theory.

    If `theory` is not given, assumes the top theory.

    Returns:
       `theory` or the top theory.
    """
    from .theory import Theory
    return Theory._thy(theory)


def EmptyTheory(**kwargs):
    """Creates an empty theory.

    An empty theory is one containing no extensions (not even those added by
    the standard prelude).

    Returns:
       An empty theory (:class:`Theory`).
    """
    return _thy().__class__(load_prelude=False, **kwargs)  # no args


# -- Adding extensions -----------------------------------------------------

def extend(ext, theory=None):
    """Adds extension.

    See :meth:`Theory.extend`.
    """
    return _thy(theory).extend(ext)


def new_base_type(arg1, theory=None, **kwargs):
    """Adds new base type.

    See :meth:`Theory.new_base_type`.
    """
    return _thy(theory).new_base_type(arg1, **kwargs)


def new_type_constructor(arg1, arg2, arg3=None, theory=None, **kwargs):
    """Adds new type constructor.

    See :meth:`Theory.new_type_constructor`.
    """
    return _thy(theory).new_type_constructor(arg1, arg2, arg3, **kwargs)


def new_constant(arg1, arg2, theory=None, **kwargs):
    """Adds new (primitive) constant.

    See :meth:`Theory.new_constant`.
    """
    return _thy(theory).new_constant(arg1, arg2, **kwargs)


def new_axiom(arg1, arg2=None, theory=None, **kwargs):
    """Adds new axiom.

    See :meth:`Theory.new_axiom`.
    """
    return _thy(theory).new_axiom(arg1, arg2, **kwargs)


def new_definition(arg1, arg2, theory=None, **kwargs):
    """Adds new definition.

    See :meth:`Theory.new_definition`.
    """
    return _thy(theory).new_definition(arg1, arg2, **kwargs)


def new_theorem(arg1, arg2=None, theory=None, **kwargs):
    """Adds new theorem.

    See :meth:`Theory.new_theorem`.
    """
    return _thy(theory).new_theorem(arg1, arg2, **kwargs)


def new_python_type_alias(arg1, arg2, arg3=None, theory=None, **kwargs):
    """Adds new Python type alias.

    See :meth:`Theory.new_python_type_alias`.
    """
    return _thy(theory).new_python_type_alias(arg1, arg2, arg3, **kwargs)[1]


# -- Removing extensions ---------------------------------------------------

def reset(arg=None, theory=None):
    """Removes all extensions since *arg* (inclusive).

    See :meth:`Theory.reset`.
    """
    return _thy(theory).reset(arg)


# -- Querying extensions ---------------------------------------------------

def enumerate_extensions(*args, theory=None, **kwargs):
    """Enumerates extensions matching criteria.

    See :meth:`Theory.enumerate_extensions`.
    """
    return _thy(theory).enumerate_extensions(*args, **kwargs)


def lookup_extension(*args, theory=None, **kwargs):
    """Searches for extension.

    See :meth:`Theory.lookup_extension`.
    """
    return _thy(theory).lookup_extension(*args, **kwargs)


def lookup_type_constructor(*args, theory=None, **kwargs):
    """Searches for type constructor.

    See :meth:`Theory.lookup_type_constructor`.
    """
    return _thy(theory).lookup_type_constructor(*args, **kwargs)


def lookup_constant(*args, theory=None, **kwargs):
    """Searches for constant.

    See :meth:`Theory.lookup_constant`.
    """
    return _thy(theory).lookup_constant(*args, **kwargs)


def lookup_axiom(*args, theory=None, **kwargs):
    """Searches for axiom.

    See :meth:`Theory.lookup_axiom`.
    """
    return _thy(theory).lookup_axiom(*args, **kwargs)


def lookup_definition(*args, theory=None, **kwargs):
    """Searches for definition.

    See :meth:`Theory.lookup_definition`.
    """
    return _thy(theory).lookup_definition(*args, **kwargs)


def lookup_theorem(*args, theory=None, **kwargs):
    """Searches for theorem.

    See :meth:`Theory.lookup_theorem`.
    """
    return _thy(theory).lookup_theorem(*args, **kwargs)


def lookup_python_type_alias(*args, theory=None, **kwargs):
    """Searches for Python type alias.

    See :meth:`Theory.lookup_python_type_alias`.
    """
    return _thy(theory).lookup_python_type_alias(*args, **kwargs)


def lookup_python_type_alias_spec(*args, theory=None, **kwargs):
    """Searches for Python type alias specification.

    See :meth:`Theory.lookup_python_type_alias_spec`.
    """
    return _thy(theory).lookup_python_type_alias_spec(*args, **kwargs)


# -- Showing extensions ----------------------------------------------------

def show_extensions(*args, theory=None, **kwargs):
    """Prints extensions matching criteria.

    See :meth:`Theory.show_extensions`.
    """
    return _thy(theory).show_extensions(*args, **kwargs)


def show_type_constructors(*args, theory=None, **kwargs):
    """Prints type constructors matching criteria.

    See :meth:`Theory.show_extensions`.
    """
    thy = _thy(theory)
    return thy.show_extensions(
        *args, class_=thy.NewTypeConstructor, **kwargs)


def show_constants(*args, theory=None, **kwargs):
    """Prints constants matching criteria.

    See :meth:`Theory.show_extensions`.
    """
    thy = _thy(theory)
    return thy.show_extensions(
        *args, class_=thy.NewConstant, **kwargs)


def show_axioms(*args, theory=None, **kwargs):
    """Prints axioms matching criteria.

    See :meth:`Theory.show_extensions`.
    """
    thy = _thy(theory)
    return thy.show_extensions(
        *args, class_=thy.NewAxiom, **kwargs)


def show_definitions(*args, theory=None, **kwargs):
    """Prints definitions matching criteria.

    See :meth:`Theory.show_extensions`.
    """
    thy = _thy(theory)
    return thy.show_extensions(
        *args, class_=thy.NewDefinition, **kwargs)


def show_theorems(*args, theory=None, **kwargs):
    """Prints theorems matching criteria.

    See :meth:`Theory.show_extensions`.
    """
    thy = _thy(theory)
    return thy.show_extensions(
        *args, class_=thy.NewTheorem, **kwargs)


def show_python_type_aliases(*args, theory=None, **kwargs):
    """Prints Python type aliases matching criteria.

    See :meth:`Theory.show_extensions`.
    """
    thy = _thy(theory)
    return thy.show_extensions(
        *args, class_=thy.NewPythonTypeAlias, **kwargs)


# -- Settings --------------------------------------------------------------

#: Settings table of the top theory.
settings = util.Proxy(lambda: _thy().settings)
