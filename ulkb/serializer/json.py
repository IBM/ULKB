# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import json

from ..converter.ast import ConverterAST_Settings
from .serializer import Serializer


class SerializerJSON_Settings(ConverterAST_Settings):
    append = False
    ensure_ascii = False
    indent = 4
    separators = (',', ':')
    sort_keys = False


class SerializerJSON(
        Serializer, format='json', format_long='JSON',
        settings=SerializerJSON_Settings):

    def __init__(self, obj, encoding=None, **kwargs):
        super().__init__(obj, encoding=encoding, **kwargs)
        self.settings = self.cls._thy().settings.serializer.json(**kwargs)

    def do_serialize_to_file(self, path):
        mode = 'a' if self.settings.append else 'w'
        with open(path, mode) as fp:
            self.do_serialize_to_stream(fp)
            print(file=fp)

    def do_serialize_to_string(self):
        return json.dumps(
            self._object_to_ast(),
            ensure_ascii=self.settings.ensure_ascii,
            indent=self.settings.indent,
            separators=self.settings.separators,
            sort_keys=self.settings.sort_keys)

    def do_serialize_to_stream(self, stream):
        json.dump(
            self._object_to_ast(),
            stream,
            ensure_ascii=self.settings.ensure_ascii,
            indent=self.settings.indent,
            separators=self.settings.separators,
            sort_keys=self.settings.sort_keys)

    def _object_to_ast(self):
        return self.obj.to_ast(
            args_tag=self.settings.args_tag,
            class_tag=self.settings.class_tag)
