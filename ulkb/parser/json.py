# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import json

from ..converter.ast import ConverterAST_Settings
from .parser import Parser


class ParserJSON_Settings(ConverterAST_Settings):
    pass


class ParserJSON(
        Parser, format='json', format_long='JSON',
        settings=ParserJSON_Settings):

    def __init__(self, cls, encoding=None, **kwargs):
        super().__init__(cls, encoding=encoding, **kwargs)
        self.settings = cls._thy().settings.parser.json(**kwargs)

    def do_parse_from_string(self, text):
        return self._cls_from_ast(json.loads(text))

    def do_parse_from_stream(self, stream):
        return self._cls_from_ast(json.load(stream))

    def _cls_from_ast(self, ast):
        return self.cls.from_ast(
            ast,
            args_tag=self.settings.args_tag,
            class_tag=self.settings.class_tag)
