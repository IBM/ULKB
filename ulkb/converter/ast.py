# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .. import util
from ..settings import Settings
from .converter import Converter, ConverterError


class ConverterAST_Settings(Settings):
    args_tag = 'args'
    class_tag = 'class'


class ConverterAST(
        Converter, format='ast', format_long='AST',
        settings=ConverterAST_Settings):

    def __init__(self, cls, arg, **kwargs):
        super().__init__(cls, arg, **kwargs)
        # settings
        self.settings = cls._thy().settings.converter.ast(**kwargs)
        self.args_tag = self.settings.args_tag
        self.class_tag = self.settings.class_tag
        # internal attributes
        self.tags = {self.args_tag, self.class_tag}

    def do_convert_from(self):
        return self._do_convert_from(self.arg)

    def _do_convert_from(self, ast):
        if not isinstance(ast, dict):
            return ast
        if self.class_tag not in ast:
            raise self.error(f"missing required field '{self.class_tag}'")
        if not hasattr(self.cls, ast[self.class_tag]):
            raise self.error(f"invalid class '{ast[self.class_tag]}'")
        cls = getattr(self.cls, ast[self.class_tag])
        if self.args_tag not in ast:
            raise self.error(f"missing required field '{self.args_tag}'")
        args = map(self._do_convert_from, ast[self.args_tag])
        try:
            return cls._dup(*args, **dict(util.starmap(
                self._do_convert_from_contract,
                filter(self._do_convert_from_filter, ast.items()))))
        except ConverterError as err:
            raise err
        except Exception as err:
            raise self.error(f'{cls.__name__}: {err}')

    def _do_convert_from_filter(self, t):
        return t[0] not in self.tags

    def _do_convert_from_contract(self, k, v):
        if (isinstance(v, dict)
            and self.class_tag in v
            and getattr(self.cls, v[self.class_tag])
                and self.args_tag in v):
            return k, self._do_convert_from(v)
        else:
            return k, v

    def do_convert_to(self):
        return self._do_convert_to(self.arg)

    def _do_convert_to(self, obj):
        if not self.cls.Object.test(obj):  # ensure JSON-compatibility
            if isinstance(obj, (set, frozenset)):
                return list(obj)
            elif isinstance(obj, type):
                return str(obj.__name__)
            else:
                return obj
        return {
            self.class_tag: obj.__class__.__name__,
            self.args_tag: tuple(map(self._do_convert_to, obj.args)),
            **dict(util.starmap(
                self._do_convert_to_expand, obj.annotations.items()))}

    def _do_convert_to_expand(self, k, v):
        if self.cls.Object.test(v):
            return k, self._do_convert_to(v)
        else:
            return k, v
