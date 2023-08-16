# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import importlib
import sys

from . import error, util
from .expression import *
from .extension import *
from .object import *
from .rule import RuleAxiom
from .theory_settings import *

__all__ = [
    'Theory',
]


class Theory(Object):
    """The state of the logic developments so far.

    A :class:`Theory` consists of a sequence of extensions
    (:class:`Extension`).

    Multiple :class:`Theory` objects can coexist, but at any time only one
    of them is the current or *top* theory.  By default, :doc:`commands
    <commands>` and other top-level functions operate over the top theory.

    The top theory can be accessed using :attr:`Theory.top` or :func:`_thy`.
    It can be changed using :func:`Theory.push` and restored using
    :func:`Theory.pop`.

    Parameters:
       args: Extensions.
       load_prelude: Whether to load the standard prelude.
       kwargs: Annotations.

    Returns:
       :class:`Theory`.
    """

    #: The top theory.
    top = None

    #: Theory stack.
    _stack = []

    #: Prefix of the prelude module (initialized by __init__.py).
    _prelude_prefix = None

    @classmethod
    def _dup(cls, *args, **kwargs):
        return cls(*args, load_prelude=False, **kwargs)

    @classmethod
    def _check_args(cls, self, *args, theory=None):
        if not isinstance(self, Theory):
            thy = theory if theory is not None else cls._thy()
            args = (self, *args)
        else:
            thy = self
        return thy, args

    @classmethod
    def push(cls, theory):
        """Pushes `theory` onto theory stack.

        Makes `theory` the new top theory.

        Parameters:
           theory: :class:`Theory`.

        Returns:
           `theory`.
        """
        cls._stack.append(theory)
        cls.top = theory
        return theory

    @classmethod
    def pop(cls):
        """Pops theory from theory stack.

        Makes the theory immediately below the popped one the new top
        theory.

        Returns:
           The popped theory.
        """
        assert len(cls._stack) > 1
        theory = cls._stack.pop()
        cls.top = cls._stack[-1]
        return theory

    __slots__ = (
        '_cached_ids',
        '_cached_type_constructors',
        '_cached_type_constructors_dict',
        '_cached_constants',
        '_cached_constants_dict',
        '_cached_axioms_dict',
        '_cached_definitions_dict',
        '_cached_theorems_dict',
        '_cached_python_type_aliases_dict',
        '_cached_python_type_alias_specs_dict',
        '_cached_type_specs_dict',
        '_prelude',
        '_prelude_offset',
        '_settings',
    )

    def __init__(self, *args, load_prelude=True, **kwargs):
        super().__init__(**kwargs)
        self._settings = TheorySettings()
        if load_prelude:
            self._prelude = self._load_prelude()
            self._prelude_offset = len(self.args)
        else:
            self._prelude = None
            self._prelude_offset = 0
        for ext in args:
            self._extend(ext)

    def __enter__(self):
        return self.push(self)

    def __exit__(self, err_type, err_val, err_bt):
        if err_val is not None:
            raise err_val
        else:
            return self.pop()

    def _set_args(self, args):
        self._args = list(args)  # make args mutable

    def _reset_object_caches(self):
        self._hash = None
        self._hexdigest = None

    def _build_ids_cache(self):
        return dict()

    def _build_type_constructors_cache(self):
        return set()

    def _build_type_constructors_dict_cache(self):
        return dict()

    def _build_constants_cache(self):
        return set()

    def _build_constants_dict_cache(self):
        return dict()

    def _build_axioms_dict_cache(self):
        return dict()

    def _build_definitions_dict_cache(self):
        return dict()

    def _build_theorems_dict_cache(self):
        return dict()

    def _build_python_type_aliases_dict_cache(self):
        return dict()

    def _build_python_type_alias_specs_dict_cache(self):
        return dict()

    def _build_type_specs_dict_cache(self):
        return dict()

    # -- Modules -----------------------------------------------------------

    def load(self, mod_name):
        """Loads module into theory.

        Parameters:
           mod_name: Module name.

        Returns:
           The loaded module.
        """
        with self:
            if mod_name in sys.modules:
                importlib.reload(sys.modules[mod_name])
            else:
                importlib.import_module(mod_name)
        return sys.modules[mod_name]

    # -- Prelude -----------------------------------------------------------

    def _load_prelude(self):
        from types import ModuleType
        mod = self.load(self._prelude_prefix + '.prelude')
        for k in dir(mod):
            v = getattr(mod, k)
            if isinstance(v, ModuleType):
                self.load(v.__name__)
        return mod

    @property
    def prelude(self):
        """Prelude module or ``None`` (not loaded)."""
        return self.get_prelude()

    def get_prelude(self):
        """Gets prelude module.

        Returns:
           Prelude module or ``None`` (not loaded).
        """
        return self._prelude

    @property
    def prelude_offset(self):
        """Start index of non-prelude extensions."""
        return self.get_prelude_offset()

    def get_prelude_offset(self):
        """Gets start index of non-prelude extensions.

        Returns:
           Start index of non-prelude extensions.
        """
        return self._prelude_offset

    @property
    def args_no_prelude(self):
        """Theory arguments excluding prelude extensions."""
        return self.get_args_no_prelude()

    def get_args_no_prelude(self):
        """Gets theory arguments excluding prelude extensions.

        Returns:
           Theory arguments excluding prelude extensions.
        """
        return self[self._prelude_offset:]

    # -- Settings ----------------------------------------------------------

    @property
    def settings(self):
        """Theory settings table.

        See also:
           :class:`ulkb.theory_settings.TheorySettings`.
        """
        return self.get_settings()

    def get_settings(self):
        """Gets theory settings table.

        Returns:
           Theory settings table.

        See also:
           :class:`ulkb.theory_settings.TheorySettings`.
        """
        return self._settings

    # -- Adding extensions -------------------------------------------------

    def extend(self, ext):
        """Adds extension.

        Parameters:
           ext: :class:`Extension`.

        Returns:
           `ext`.

        Raises:
           ExtensionError: `ext` cannot be added to theory.

        See also:
           :func:`extend`.
        """
        return self._extend(Extension.check(ext))

    def _extend(
            self, ext, func_name=None, arg_name=None, arg_position=None):
        if ext in self.args:
            return ext          # nothing to do
        if ext.id is not None and ext.id in self.ids:
            raise ext.error(f"extension '{ext.id}' already exists")
        if ext.is_new_type_constructor():
            pass
        elif ext.is_new_constant():
            (const,) = ext._unpack_new_constant()
            self._check_extension_types(ext, const.type)
        elif ext.is_new_axiom():
            const, form = ext._unpack_new_axiom()
            self._check_extension_types(ext, form)
            self._cache_extension(NewConstant(const))
        elif ext.is_new_definition():
            (form,) = ext._unpack_new_definition()
            l, r = form._unpack_equal()
            self._check_extension_types(ext, form)
            self._cache_extension(NewConstant(Constant(l.id, l.type)))
            self._check_extension_constants(ext, r)
        elif ext.is_new_theorem():
            const, seq = ext._unpack_extension()
            for form in util.chain(seq.hypotheses, [seq.conclusion]):
                self._check_extension_types(ext, form)
            self._cache_extension(NewConstant(const))
        elif ext.is_new_python_type_alias():
            (_, type, spec) = ext._unpack_new_python_type_alias()
            self._check_extension_types(ext, type)
            if spec is not None and not hasattr(self, spec):
                raise ext.error(f"undefined type alias spec '{spec}'")
        elif ext.is_new_type_spec():
            (spec,) = ext._unpack_new_type_spec()
            if not hasattr(self, spec):
                raise ext.error(f"undefined type spec '{spec}'")
        else:
            error.should_not_get_here()
        self._cache_extension(ext)
        self.args.append(ext)
        return ext

    def _check_extension_constants(self, ext, term):
        for c in term.constants:
            if (c.id not in self.constants_dict
                or not util.any_map(
                    lambda x: c.type.matches(x.type), term.constants)):
                raise ext.error(f"undefined constant '{c}'")
        return term

    def _check_extension_types(self, ext, term):
        if term.type_constructors <= self.type_constructors:
            return term
        else:
            msg = error._build_plural_message(
                'undefined type constructor%s',
                *(term.type_constructors - self.type_constructors))
            raise ext.error(msg)

    def _cache_extension(self, ext):
        if ext.id is not None:
            self.ids[ext.id] = ext
        if ext.is_new_type_constructor():
            (tcons,) = ext._unpack_new_type_constructor()
            self.type_constructors.add(tcons)
            self.type_constructors_dict[tcons] = tcons
            self.type_constructors_dict[tcons.id] = tcons
        elif ext.is_new_constant():
            (const,) = ext._unpack_new_constant()
            self.constants.add(const)
            self.constants_dict[const] = const
            self.constants_dict[const.id] = const
        elif ext.is_new_axiom():
            const, form = ext._unpack_new_axiom()
            seq = RuleAxiom(form)
            self.axioms_dict[const] = seq
            self.axioms_dict[const.id] = seq
        elif ext.is_new_definition():
            (form,) = ext._unpack_new_definition()
            l, r = form._unpack_equal()
            const = self.constants_dict[l.id]
            seq = RuleAxiom(self.Equal(const, r))
            self.definitions_dict[const] = seq
            self.definitions_dict[const.id] = seq
        elif ext.is_new_theorem():
            const, seq = ext._unpack_new_theorem()
            self.theorems_dict[const] = seq
            self.theorems_dict[const.id] = seq
        elif ext.is_new_python_type_alias():
            py_type, type, spec = ext._unpack_new_python_type_alias()
            self.python_type_aliases_dict[py_type.__name__] = type
            self.python_type_aliases_dict[py_type] = type
            if spec is not None:
                spec = getattr(self, spec)
                self.python_type_alias_specs_dict[py_type.__name__] = spec
                self.python_type_alias_specs_dict[py_type] = spec
        elif ext.is_new_type_spec():
            (spec,) = ext._unpack_new_type_spec()
            spec = getattr(self, spec)
            self.type_specs_dict[spec.constructor.id] = spec
            self.type_specs_dict[spec.constructor] = spec
        else:
            error.should_not_get_here()
        self._reset_object_caches()

    def _uncache_extension(self, ext):
        if ext.id is not None:
            self.ids.pop(ext.id)
        if ext.is_new_type_constructor():
            (tcons,) = ext._unpack_new_type_constructor()
            self.type_constructors.remove(tcons)
            self.type_constructors_dict.pop(tcons)
            self.type_constructors_dict.pop(tcons.id)
        elif ext.is_new_constant():
            (const,) = ext._unpack_new_constant()
            self._uncache_constant(const)
        elif ext.is_new_axiom():
            const, form = ext._unpack_new_axiom()
            self._uncache_constant(const)
            self.axioms_dict.pop(const)
            self.axioms_dict.pop(const.id)
        elif ext.is_new_definition():
            (form,) = ext._unpack_new_definition()
            l, _ = form._unpack_equal()
            const = self.lookup_constant(l.id)
            self._uncache_constant(const)
            self.definitions_dict.pop(const)
            self.definitions_dict.pop(const.id)
        elif ext.is_new_theorem():
            const, _ = ext._unpack_new_theorem()
            self._uncache_constant(const)
            self.theorems_dict.pop(const)
            self.theorems_dict.pop(const.id)
        elif ext.is_new_python_type_alias():
            py_type, _, spec = ext._unpack_new_python_type_alias()
            self.python_type_aliases_dict.pop(py_type.__name__)
            self.python_type_aliases_dict.pop(py_type)
            if spec is not None:
                self.python_type_alias_specs_dict.pop(py_type.__name__)
                self.python_type_alias_specs_dict.pop(py_type)
        else:
            error.should_not_get_here()
        self._reset_object_caches()

    def _uncache_constant(self, const):
        self.constants.remove(const)
        self.constants_dict.pop(const)
        self.constants_dict.pop(const.id)

    def new_base_type(self, arg1, **kwargs):
        """Adds new base type.

        Parameters:
           arg1: Id.
           kwargs: Annotations.

        Returns:
           :class:`TypeApplication`.

        .. code-block:: python
           :caption: Equivalent to:

           self.extend(NewTypeConstructor(
              TypeConstructor(arg1, 0, None, **kwargs)))[0]()

        See also:
           :func:`new_base_type`.
        """
        return self.new_type_constructor(arg1, 0, None, **kwargs)()

    def new_type_constructor(self, arg1, arg2, arg3=None, **kwargs):
        """Adds new type constructor.

        Parameters:
           arg1: Id.
           arg2: Arity.
           arg3: Associativity (``'left'`` or ``'right'``).
           kwargs: Annotations.

        Returns:
           :class:`TypeConstructor`.

        .. code-block:: python
           :caption: Equivalent to:

           self.extend(NewTypeConstructor(
              TypeConstructor(arg1, arg2, arg3, **kwargs)))[0]

        See also:
           :func:`new_type_constructor`.
        """
        return self._extend(NewTypeConstructor(
            TypeConstructor(arg1, arg2, arg3, **kwargs)))[0]

    def new_constant(self, arg1, arg2, **kwargs):
        """Adds new constant.

        Parameters:
           arg1: Id.
           arg2: :class:`Type`.
           kwargs: Annotations.

        Returns:
           :class:`Constant`.

        .. code-block:: python
           :caption: Equivalent to:

           self.extend(NewConstant(Constant(arg1, arg2, **kwargs)))[0]

        See also:
          :func:`new_constant`.
        """
        return self._extend(NewConstant(Constant(arg1, arg2, **kwargs)))[0]

    def new_axiom(self, arg1, arg2=None, **kwargs):
        """Adds new axiom.

        If `arg2` is not given, uses `arg1` to generate an id.

        Parameters:
           arg1: Id or :class:`Formula`.
           arg2: :class:`Formula`.
           kwargs: Annotations.

        Returns:
           :class:`Sequent`.

        .. code-block:: python
           :caption: Equivalent to:

           self.extend(NewAxiom(
              Constant(arg1, arg2.type), arg2, **kwargs));
           self.axioms_dict[arg1]

        See also:
           :func:`new_axiom`.
        """
        if arg2 is None:
            arg2, arg1 = arg1, arg1._as_id()
        self._extend(NewAxiom(Constant(arg1, arg2.type), arg2, **kwargs))
        return self.axioms_dict[arg1]

    def new_definition(self, arg1, arg2, **kwargs):
        """Adds new definition.

        Parameters:
           arg1: Id.
           arg2: :class:`Term`.
           kwargs: Annotations.

        Returns:
           :class:`Constant`.

        .. code-block:: python
           :caption: Equivalent to:

           self.extend(NewDefinition(
              Equal(Constant(arg1, arg2.type), arg2), **kwargs));
           self.constants_dict[arg1]

        See also:
           :func:`new_definition`.
        """
        self._extend(NewDefinition(
            self.Equal(Variable(arg1, arg2.type), arg2), **kwargs))
        return self.constants_dict[arg1]

    def new_theorem(self, arg1, arg2=None, **kwargs):
        """Adds new theorem.

        If `arg2` is not given, uses `arg1` to generate an id.

        Parameters:
           arg1: Id or :class:`Sequent`.
           arg2: :class:`Sequent`.
           kwargs: Annotations.

        Returns:
           :class:`Sequent`

        .. code-block:: python
           :caption: Equivalent to:

           extend(NewTheorem(
              Constant(arg1, BoolType()), arg2), **kwargs));
           self.theorems_dict[arg1]

        See also:
           :func:`new_theorem`.
        """
        if arg2 is None:
            arg2, arg1 = arg1, arg1._as_id()
        self._extend(NewTheorem(Constant(arg1, bool), arg2, **kwargs))
        return self.theorems_dict[arg1]

    def new_python_type_alias(self, arg1, arg2, arg3=None, **kwargs):
        """Adds new Python type alias.

        Parameters:
           arg1: Python type.
           arg2: :class:`Type`.
           arg3: Type specification.
           kwargs: Annotations.

        Returns:
           :class:`Type`.

        .. code-block:: python
           :caption: Equivalent to:

           extend(NewPythonTypeAlias(arg1, arg2, **kwargs))[1]

        See also:
           :func:`new_python_type_alias`.
        """
        return self._extend(NewPythonTypeAlias(arg1, arg2, arg3, **kwargs))

    # -- Removing extensions -----------------------------------------------

    def reset(self, arg=None):
        """Removes all extensions since *arg* (inclusive).

        If `arg` is an id, goes back to the extension preceding the one
        introducing the object with id `arg`.

        If `arg` is an object, goes back to the extension preceding the one
        introducing `arg`.

        If `arg` is a non-negative integer, goes back to the extension
        preceding the one at offset `arg`.

        If `arg` is a negative integer, drops the last `abs(arg)`
        extensions.

        If `arg` is not given, goes back to the initial state; i.e., makes
        `arg` equal to :attr:`Theory.prelude_offset`.

        Parameters:
           arg: Id, :class:`Object`, or int.

        Returns:
           The number of extensions removed.

        Raises:
           LookupError: `arg` not in theory.
        """
        if arg is None:
            start = self.prelude_offset
        elif isinstance(arg, int):
            if arg >= 0:
                start = arg
            else:
                start = len(self.args) + arg
        elif Object.test(arg):
            if Extension.test(arg) and arg in self.args:
                start = self.args.index(arg)
            elif hasattr(arg, 'id'):
                start = self.args.index(self.lookup_extension(arg.id))
            else:
                raise LookupError(f"no such extension '{arg}'")
        else:                   # arg is an id
            start = self.args.index(self.lookup_extension(arg))
        if start < self.prelude_offset:
            self._prelude_offset = start
        n = len(self.args)
        for i in range(n - 1, start - 1, -1):
            ext = self.args[i]
            self._uncache_extension(ext)
            self.args.pop()
        return n - start

    # -- Querying extensions -----------------------------------------------

    def enumerate_extensions(
            self, *args, limit=None, offset=None, id=None, class_=None):
        """Enumerates extensions matching criteria.

        If `offset` is not given, assumes :attr:`Theory.prelude_offset`.

        Parameters:
           args: Expressions that must occur in extension.
           limit: Maximum number of results.
           offset: Minimum offset.
           id: Id (regex).
           class_: Class.

        Returns:
           An iterator of index-:class:`Extension` pairs.

        See also:
           :func:`enumerate_extensions`.
        """
        offset = offset if offset is not None else self._prelude_offset
        if id is not None:
            _id_re = util.compile(id)
        if class_ is not None:
            error.check_arg_is_type(
                class_, 'enumerate_extensions', 'class_')
        if args:
            args_cts, args_tcs = set(), set()
            for i, arg in enumerate(args):
                if isinstance(arg, type):
                    try:
                        arg = self.lookup_python_type_alias(arg)
                    except:
                        pass
                Expression.check(arg, 'enumerate_extensions', None, i)
                if arg.is_term():
                    args_cts.update(arg.constants)
                args_tcs.update(arg.type_constructors)
        n = 0
        for i, x in enumerate(self[offset:]):
            if id and (not x.id or not _id_re.match(x.id)):
                continue
            if class_ and not isinstance(x, class_):
                continue
            if args:
                if args_cts:
                    cts = set.union(set(), *map(
                        lambda t: t.constants, filter(Term.test, x.args)))
                    if args_cts.isdisjoint(cts):
                        continue
                if args_tcs:
                    tcs = set.union(set(), *map(
                        lambda t: t.type_constructors,
                        filter(Expression.test, x.args)))
                    if not (args_tcs & tcs):
                        continue
            if limit is not None and n >= limit:
                break
            n += 1
            yield (offset + i, x)

    def _lookup(self, dict_, target, arg, default):
        obj = dict_.get(arg, default)
        if obj is not util.Nil:
            return obj
        else:
            raise LookupError(f"no such {target} '{arg}'")

    def lookup_extension(self, arg, default=util.Nil):
        """Searches for extension.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id.
           default: Value.

        Returns:
           :class:`Extension`.

        Raises:
           LookupError: `arg` not in theory.

        See also:
           :func:`lookup_extension`.
        """
        return self._lookup(self.ids, 'extension', arg, default)

    def lookup_type_constructor(self, arg, default=util.Nil):
        """Searches for type constructor.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id or :class:`TypeConstructor`.
           default: Value.

        Returns:
           :class:`TypeConstructor`.

        Raises:
           LookupError: `arg` not in theory.

        See also:
           :func:`lookup_type_constructor`.
        """
        return self._lookup(
            self.type_constructors_dict, 'type constructor', arg, default)

    def lookup_constant(self, arg, default=util.Nil):
        """Searches for constant.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id or :class:`Constant`.
           default: Value.

        Returns:
           :class:`Constant`.

        Raises:
           LookupError: `arg` not in theory.

        See also:
           :func:`lookup_constant`.
        """
        return self._lookup(self.constants_dict, 'constant', arg, default)

    def lookup_axiom(self, arg, default=util.Nil):
        """Searches for axiom.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id or :class:`Constant`.
           default: Value.

        Returns:
           :class:`Sequent`.

        Raises:
           LookupError: `arg` not in theory.

        See also:
           :func:`lookup_axiom`.
        """
        return self._lookup(self.axioms_dict, 'axiom', arg, default)

    def lookup_definition(self, arg, default=util.Nil):
        """Searches for definition.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id or :class:`Constant`.
           default: Value.

        Returns:
           :class:`Sequent`.

        Raises:
           LookupError: `arg` not in theory.

        See also:
           :func:`lookup_definition`.
        """
        return self._lookup(
            self.definitions_dict, 'definition', arg, default)

    def lookup_theorem(self, arg, default=util.Nil):
        """Searches for theorem.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id or :class:`Constant`.
           default: Value.

        Returns:
           :class:`Sequent`.

        Raises:
           LookupError: `arg` not in theory.

        See also:
           :func:`lookup_theorem`.
        """
        return self._lookup(
            self.theorems_dict, 'theorem', arg, default)

    def lookup_python_type_alias(self, arg, default=util.Nil):
        """Searches for Python type alias.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id.
           default: Value.

        Returns:
           :class:`Type`.

        Raises:
           LookupError: `arg` not in theory.

        See also:
           :func:`lookup_python_type_alias`.
        """
        return self._lookup(
            self.python_type_aliases_dict, 'type alias', arg, default)

    def lookup_python_type_alias_spec(self, arg, default=util.Nil):
        """Searches for Python type alias specification.

        If `default` is given, returns it instead of raising an exception.

        Parameters:
           arg: Id.
           default: Value.

        Returns:
           Type specification.

        Raises:
           LookupError: `arg` not in theory.
        """
        return self._lookup(
            self.python_type_alias_specs_dict,
            'type alias spec', arg, default)

    # -- Showing extensions ------------------------------------------------

    def show_extensions(
            self, *args, limit=None, offset=None, id=None, class_=None,
            **kwargs):
        """Prints extensions matching criteria.

        If `offset` is not given, assumes :attr:`Theory.prelude_offset`.

        Parameters:
           args: Expressions that must occur in extension.
           limit: Maximum number of results.
           offset: Minimum offset.
           id: Id (regex).
           class_: Class.
           kwargs: Extra arguments to be passed to :func:`print`.

        See also:
           :func:`show_extensions`, :func:`show_type_constructors`,
           :func:`show_constants`, :func:`show_axioms`,
           :func:`show_definitions`, :func:`show_theorems`,
           :func:`show_python_type_aliases`.
        """
        sep = kwargs.pop('sep', '\t')
        for i, ext in self.enumerate_extensions(
                *args, limit=limit, offset=offset, id=id, class_=class_):
            print(i, ext, sep=sep, **kwargs)


Theory.push(Theory(load_prelude=False))
