# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from abc import ABCMeta, abstractmethod
from collections.abc import Sequence

from . import error, util

__all__ = [
    'Object',
]


class ObjectMeta(ABCMeta):

    _object_class = None

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        mcls._init(cls, name, bases, namespace, **kwargs)
        return cls

    @classmethod
    def _init(mcls, cls, name, bases, namespace, **kwargs):
        top = mcls._object_class or cls
        setattr(top, name, cls)
        cls.name = util.camel2snake(name)
        mcls._init_is_(top, cls)
        mcls._init_test_(top, cls)
        mcls._init_check_(top, cls)
        mcls._init_unfold_(top, cls)
        mcls._init_unpack_(top, cls)
        mcls._init_preprocess_arg_(top, cls)
        mcls._init_cached_(top, cls)
        if top == cls:          # execute only once, for top
            mcls._init_converters(top)
            mcls._init_parsers(top)
            mcls._init_serializers(top)
        return cls

    @classmethod
    def _init_is_(mcls, top, cls):
        setattr(top, 'is_' + cls.name, lambda x: cls.test(x))

    @classmethod
    def _init_test_(mcls, top, cls):
        def f_test(arg):
            return cls.test(arg)
        f_test.__doc__ = f"""\
        Tests whether object is an instance of :class:`{cls.__name__}`.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        setattr(top, 'test_' + cls.name, f_test)

    @classmethod
    def _init_check_(mcls, top, cls):
        def mk_check_(s):
            def check_(arg, func_name=s, arg_name=None, arg_position=None):
                return cls.check(arg, func_name, arg_name, arg_position)
            return check_
        s = 'check_' + cls.name
        f_check = mk_check_(s)
        f_check.__doc__ = f"""\
        Checks whether object is an instance of :class:`{cls.__name__}`.

        Parameters:
           func_name: Function name.
           arg_name: Argument name.
           arg_position: Argument position.

        Returns:
           :class:`{cls.__name__}`.

        Raises:
           TypeError: Object is not an instance of :class:`{cls.__name__}`.
        """
        setattr(top, s, f_check)

    @classmethod
    def _init_unfold_(mcls, top, cls):
        def f_unfold(arg):
            return cls.unfold(arg)
        f_unfold.__doc__ = f"""\
        Unfolds arguments of :class:`{cls.__name__}`.

        Returns:
           :class:`{cls.__name__}`'s arguments unfolded.

        Raises:
           TypeError: Object is not an instance of :class:`{cls.__name__}`.
        """

        def f_unfold_unsafe(arg):
            return cls.unfold_unsafe(arg)
        f_unfold_unsafe.__doc__ = f"""\
        Unfolds arguments of :class:`{cls.__name__}` (unsafe version).

        Returns:
           :class:`{cls.__name__}`'s arguments unfolded if object is an
           instance of :class:`{cls.__name__}`; ``None`` otherwise.
        """

        s = 'unfold_' + cls.name
        setattr(top, s, f_unfold)
        setattr(top, s + '_unsafe', f_unfold_unsafe)
        setattr(top, '_' + s, lambda x: cls._unfold(x))

    @classmethod
    def _init_unpack_(mcls, top, cls):
        def f_unpack(arg):
            return cls.unpack(arg)
        f_unpack.__doc__ = f"""\
        Unpacks arguments of :class:`{cls.__name__}`.

        Returns:
           :class:`{cls.__name__}`'s arguments unpacked.

        Raises:
           TypeError: Object is not an instance of :class:`{cls.__name__}`.
        """

        def f_unpack_unsafe(arg):
            return cls.unpack_unsafe(arg)
        f_unpack_unsafe.__doc__ = f"""\
        Unpacks arguments of :class:`{cls.__name__}` (unsafe version).

        Returns:
           :class:`{cls.__name__}`'s arguments unpacked if object is an
           instance of :class:`{cls.__name__}`; ``None`` otherwise.
        """

        s = 'unpack_' + cls.name
        setattr(top, s, f_unpack)
        setattr(top, s + '_unsafe', f_unpack_unsafe)
        setattr(top, '_' + s, lambda x: cls._unpack(x))

    @classmethod
    def _init_preprocess_arg_(mcls, top, cls):
        s = '_preprocess_arg_' + cls.name
        if hasattr(cls, s):
            setattr(top, s, staticmethod(getattr(cls, s)))
        else:
            def mk__preprocess_arg_(c):
                def _preprocess_arg_(self, arg, i):
                    return c.check(arg, self.__class__.__name__, None, i)
                return _preprocess_arg_
            setattr(top, s, staticmethod(mk__preprocess_arg_(cls)))

    @classmethod
    def _init_cached_(mcls, top, cls):
        setattr(cls, '_cached', list(filter(
                lambda x: x.startswith('_cached_'), cls.__dict__)))
        if cls._cached:
            def mk__init_cached(cached):
                def _init_cached(self):
                    super(cls, self)._init_cached()
                    for attr in cached:
                        setattr(self, attr, None)
                return _init_cached
            setattr(cls, '_init_cached', mk__init_cached(cls._cached))

            def mk_get_cached(x, suffix, _get):
                def get_cached(self):
                    if getattr(self, x) is None:
                        setattr(self, x, _get(self))
                    return getattr(self, x)
                return get_cached
            for attr in cls._cached:
                suffix = attr[8:]
                f_build = getattr(cls, '_build_' + suffix + '_cache')
                f_get = mk_get_cached(attr, suffix, f_build)
                f_get.__doc__ = f_build.__doc__
                setattr(cls, 'get_' + suffix, f_get)
                f_get_prop = mk_get_cached(attr, suffix, f_build)
                doc = f_build.__doc__
                if doc:
                    doc = doc[9].capitalize() + doc[10:]
                f_get_prop.__doc__ = doc
                setattr(cls, suffix, property(f_get_prop))

    @classmethod
    def _init_converters(mcls, top):
        from .converter import Converter
        for format, v in Converter.converters.items():
            def mk_from_(fmt):
                def from_(obj_cls, value, **kwargs):
                    return obj_cls.convert_from(
                        value, format=fmt, **kwargs)
                return from_
            format_long = v.get('format_long', format)
            f_from = mk_from_(format)
            f_from.__doc__ = f"""\
            Converts {format_long} `value` to object.

            Parameters:
               value: {format_long} value.
               kwargs: Options to converter.

            Returns:
               The resulting :class:`Object`.
            """
            setattr(top, 'from_' + format, classmethod(f_from))

            def mk_to_(fmt):
                def to_(self, **kwargs):
                    return self.convert_to(format=fmt, **kwargs)
                return to_
            f_to = mk_to_(format)
            f_to.__doc__ = f"""\
            Converts object to {format_long} value.

            Parameters:
               kwargs: Options to converter.

            Returns:
               The resulting {format_long} value.
            """
            setattr(top, 'to_' + format, f_to)

    @classmethod
    def _init_parsers(mcls, top):
        from .parser import Parser
        for format, v in Parser.parsers.items():
            def mk_from_(fmt):
                def from_(
                        obj_cls, from_=None, path=None, encoding=None,
                        **kwargs):
                    return obj_cls.parse(
                        from_=from_, path=path,
                        encoding=encoding, format=fmt, **kwargs)
                return from_
            format_long = v.get('format_long', format)
            f_from = mk_from_(format)
            f_from.__doc__ = f"""\
            Parses {format_long} stream into object.

            Parameters:
               from_: Source string or stream object.
               path: Source file path.
               encoding: Encoding.
               kwargs: Options to parser.

            Returns:
               The resulting :class:`Object`.
            """
            setattr(top, 'from_' + format, classmethod(f_from))

    @classmethod
    def _init_serializers(mcls, top):
        from .serializer import Serializer
        for format, v in Serializer.serializers.items():
            def mk_to_(fmt):
                def to_(obj, to=None, encoding=None, **kwargs):
                    return obj.serialize(
                        to=to, encoding=encoding, format=fmt, **kwargs)
                return to_
            format_long = v.get('format_long', format)
            f_to = mk_to_(format)
            f_to.__doc__ = f"""\
            Serializes object to {format_long} stream.

            Parameters:
               to: Target file path or stream object.
               encoding: Encoding.
               kwargs: Options to serializer.

            Returns:
               The resulting string if `to` is ``None``.  Otherwise, write
               the resulting string to `to` and returns ``None``.
            """
            setattr(top, 'to_' + format, f_to)


@util.total_ordering
class Object(Sequence, metaclass=ObjectMeta):
    """Abstract base class for syntactical objects.

    An :class:`Object` consists of a tuple of arguments :attr:`args`
    together with a dictionary of annotations :attr:`annotations`.

    Parameters:
       args: Arguments
       kwargs: Annotations.

    Returns:
       :class:`Object`.
    """

    @classmethod
    def _thy(cls, thy=None):
        return thy or cls.Theory.top

    @classmethod
    def _dup(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def _is_generated_id(cls, id):
        return id.startswith(cls._thy().settings.generated_id_prefix)

    @classmethod
    def test(cls, arg):
        """Tests whether `arg` is an instance of this class.

        Parameters:
           arg: Value.

        Returns:
           ``True`` if successful; ``False`` otherwise.
        """
        return isinstance(arg, cls)

    @classmethod
    def check(cls, arg, func_name=None, arg_name=None, arg_position=None):
        """Checks whether `arg` is an instance of this class.

        Parameters:
           arg: Value.
           func_name: Function name.
           arg_name: Argument name.
           arg_position: Argument position.

        Returns:
           `arg`.

        Raises:
           TypeError: `arg` is not an instance of this class.
        """
        return error.check_arg_class_test(
            arg, cls, cls.test(arg),
            func_name or 'check', arg_name, arg_position)

    @classmethod
    def unfold(cls, arg):
        """Unfolds `arg`'s arguments.

        Parameters:
           arg: Value.

        Returns:
           `arg`'s arguments unfolded.

        Raises:
           TypeError: `arg` is not an instance of this class.
        """
        return cls._unfold(cls.check(arg, 'unfold'))

    @classmethod
    def unfold_unsafe(cls, arg):
        """Unfolds `arg`'s arguments (unsafe version).

        Parameters:
           arg: Value.

        Returns:
           `arg`'s arguments unfolded if `arg` is an instance of this class;
           ``None`` otherwise.
        """
        return cls._unfold(arg) if cls.test(arg) else None

    @classmethod
    def _unfold(cls, arg):
        return cls._unpack(arg)

    @classmethod
    def unpack(cls, arg):
        """Unpacks `arg`'s arguments.

        Parameters:
           arg: Value.

        Returns:
           `arg`'s arguments unpacked.

        Raises:
           TypeError: `arg` is not an instance of this class.
        """
        return cls._unpack(cls.check(arg, 'unpack'))

    @classmethod
    def unpack_unsafe(cls, arg):
        """Unpacks `arg`'s arguments (unsafe version).

        Parameters:
           arg: Value.

        Returns:
           `arg`'s arguments unpacked if `arg` is an instance of this class;
           ``None`` otherwise.
        """
        return cls._unpack(arg) if cls.test(arg) else None

    @classmethod
    def _unpack(cls, arg):
        return arg.args

    __slots__ = (
        '_args',
        '_annotations',
        '_hash',
        '_hexdigest',
    )

    @abstractmethod
    def __init__(self, *args, **kwargs):
        self._init_cached()
        self._set_args(self._preprocess_args(args))
        self._set_annotations(self._preprocess_annotations(kwargs))
        self._hash = None
        self._hexdigest = None

    def _init_cached(self):
        pass

    def _set_args(self, args):
        self._args = args

    def _set_annotations(self, kwargs):
        self._annotations = kwargs

    def _preprocess_args(self, args):
        return tuple(map(
            self._preprocess_arg_callback, zip(args, util.count(1))))

    def _preprocess_arg_callback(self, t):
        return self._preprocess_arg(*t)

    def _preprocess_arg(self, arg, i):
        return error.check_arg_is_not_none(
            arg, self.__class__.__name__, None, i)

    @staticmethod
    def _preprocess_arg_id(self, arg, i):
        return error.check_arg(
            arg, arg is not None and not Object.test(arg), 'invalid id',
            self.__class__.__name__, None, i, TypeError)

    def _preprocess_annotations(self, kwargs):
        return kwargs

    @property
    def args(self):
        """Object arguments."""
        return self.get_args()

    def get_args(self):
        """Gets object arguments.

        Returns:
           Object arguments.
        """
        return self._args

    @property
    def annotations(self):
        """Object annotations."""
        return self.get_annotations()

    def get_annotations(self):
        """Gets object annotations.

        Returns:
           Object annotations.
        """
        return self._annotations

    @property
    def hexdigest(self):
        """Object hexadecimal digest."""
        return self.get_hexdigest()

    def get_hexdigest(self):
        """Gets object hexadecimal digest.

        Returns:
           Object hexadecimal digest.
        """
        if self._hexdigest is None:
            self._hexdigest = util.sha256(
                self.dump().encode('utf-8')).hexdigest()
        return self._hexdigest

    def _as_id(self):
        """Generates an unique id for object.

        Returns:
           An unique id for object.
        """
        return self._thy().settings.generated_id_prefix + self.hexdigest

    def __eq__(self, other):
        return type(self) == type(other) and self._args == other._args

    def __getitem__(self, i):
        return self.args[i]

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((self.__class__, self._args))
        return self._hash

    def __len__(self):
        return len(self.args)

    def __lt__(self, other):
        other = Object.check(other, '__lt__')
        if type(self) != type(other):
            return self.__class__.__name__ < other.__class__.__name__
        else:
            return self.args < other.args

    def __matmul__(self, kwargs):
        return self.with_annotations(**kwargs)

    def __repr__(self):
        if self._thy().settings.override_object_repr:
            return str(self)
        else:
            return super().__repr__()

    def __str__(self):
        if self._thy().settings.serializer.default is not None:
            return self.serialize()
        else:
            return self.dump()

    def dump(self):
        """Gets a raw string representation of object.

        Returns:
           A raw string representation of object.
        """
        return self._dump()

    def _dump(self, _f=(lambda x: x._dump() if Object.test(x) else str(x))):
        cls_name = self.__class__.__name__
        if self.args:
            return f'({cls_name} {" ".join(map(_f, self.args))})'
        else:
            return cls_name

    # -- Comparison --------------------------------------------------------

    def compare(self, other):
        """Compares object to `other`.

        Parameters:
           other: :class:`Object`.

        Returns:
           ``-1`` if object is less than `other`;
           ``0`` if object and `other` are equal;
           ``1`` if object is greater than `other`.

        See also:
           :meth:`Object.equal`.
        """
        if self == other:
            return 0
        elif self < other:
            return -1
        else:
            return 1

    def equal(self, other, deep=False):
        """Tests whether object is equal to `other`.

        Two objects are equal if they are instances of the same class and
        their arguments (:attr:`args`) are equal.

        If `deep` is ``True`` also compares the objects' :attr:`annotations`
        for equality.

        Parameters:
           other: :class:`Object`.
           deep: Whether to compare objects' annotations.

        Returns:
           ``True`` if successful; ``False`` otherwise.

        See also:
           :meth:`Object.deepequal`.
        """
        if self != other:
            return False
        if not deep:
            return True
        if self.annotations != other.annotations:
            return False
        for x, y in zip(self, other):  # compare args
            if isinstance(x, Object) and not x.equal(y, deep=deep):
                return False
        return True

    def deepequal(self, other):
        """Tests whether object is deep-equal to `other`.

        Two objects are deep-equal if they are instances of the same class
        and their arguments (:attr:`args`) and annotations
        (:attr:`annotations`) are deep-equal.

        Parameters:
           other: :class:`Object`.

        Returns:
           ``True`` if successful; ``False`` otherwise.

        .. code-block:: python
           :caption: Equivalent to:

           obj.equal(other, deep=True)

        See also:
           :meth:`Object.equal`.
        """
        return self.equal(other, deep=True)

    # -- Copying -----------------------------------------------------------

    def copy(self, *args, **kwargs):
        """Makes a shallow copy of object.

        If `args` are given, overwrites object arguments.

        If `kwargs` are given, overwrites object annotations.

        Parameters:
           args: Arguments.
           kwargs: Annotations.

        Returns:
           A shallow copy of object.

        See also:
           :meth:`Object.with_args`, :meth:`Object.with_annotations`.
        """
        if not args and not kwargs:
            return util.copy(self)
        else:
            args = args or self.args
            kwargs = kwargs or self.annotations
            return self._dup(*args, **kwargs)

    def with_args(self, *args):
        """Shallow-copies object overwriting its arguments.

        Parameters:
           args: Arguments.

        Returns:
           A shallow copy of object.

        .. code-block:: python
           :caption: Equivalent to:

           obj.copy(*args)

        See also:
           :meth:`Object.copy`.
        """
        return self.copy(*args)

    def with_annotations(self, **kwargs):
        """Shallow-copies object overwriting its annotations.

        Parameters:
           kwargs: Annotations.

        Returns:
           A shallow copy of object.

        .. code-block:: python
           :caption: Equivalent to:

           obj.copy(**kwargs)

        See also:
           :meth:`Object.copy`.
        """
        return self.copy(**kwargs)

    def deepcopy(self):
        """Makes a deep copy of object.

        Returns:
           A deep copy of object.
        """
        return util.deepcopy(self)

    # -- Conversion, parsing, serialization --------------------------------

    @classmethod
    def convert_from(cls, value, format=None, **kwargs):
        """Converts `value` to object.

        Parameters:
           value: Value.
           format: Source format.
           kwargs: Options to converter.

        Returns:
           The resulting object.
        """
        from .converter import Converter
        format = format or cls._thy().settings.converter.default
        format = error.check_arg_enum(
            format, Converter.converters, 'convert_from', 'format')
        return cls.check(Converter.convert_from(
            cls, value, format=format, **kwargs))

    def convert_to(self, format=None, **kwargs):
        """Converts object to value.

        Parameters:
           format: Target format.
           kwargs: Options to converter.

        Returns:
           The resulting value.
        """
        from .converter import Converter
        format = format or self._thy().settings.converter.default
        format = error.check_arg_enum(
            format, Converter.converters, 'convert_to', 'format')
        return Converter.convert_to(self, format=format, **kwargs)

    @classmethod
    def parse(
            cls, from_=None, path=None, format=None, encoding=None,
            **kwargs):
        """Parses stream into object.

        Parameters:
           from_: Source stream.
           path: Source file path.
           format: Source format.
           encoding: Encoding.
           kwargs: Options to parser.

        Returns:
           The resulting object.
        """
        from .parser import Parser
        format = format or cls._thy().settings.parser.default
        format = error.check_arg_enum(
            format, Parser.parsers, 'parse', 'format')
        return cls.check(Parser.parse(
            cls, from_=from_, path=path, format=format,
            encoding=encoding, **kwargs))

    def serialize(
            self, to=None, path=None, format=None, encoding=None, **kwargs):
        """Serializes object to stream.

        Parameters:
           to: Target stream or file path.
           path: Target file path.
           format: Target format.
           encoding: Encoding.
           kwargs: Options to serializer.

        Returns:
           The resulting stream if `to` is ``None``.  Otherwise, write
           the resulting stream to `to` and returns ``None``.
        """
        from .serializer import Serializer
        format = format or self._thy().settings.serializer.default
        format = error.check_arg_enum(
            format, Serializer.serializers, 'serialize', 'format')
        return Serializer.serialize(
            self, to=to or path, format=format, encoding=encoding, **kwargs)


ObjectMeta._object_class = Object
