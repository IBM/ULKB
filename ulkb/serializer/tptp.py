# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

import re

from .serializer import Serializer, SerializerSettings


class SerializerTPTP_Settings(SerializerSettings):
    pass


class SerializerTPTP(
        Serializer, format='tptp', format_long='TPTP',
        settings=SerializerTPTP_Settings):

    def __init__(self, obj, encoding=None, **kwargs):
        super().__init__(obj, encoding=encoding, **kwargs)
        self.settings = self.cls._thy().settings.serializer.tptp(**kwargs)

    def do_serialize_to_stream(self, stream):
        import io
        if isinstance(stream, io.TextIOBase):
            self._write = stream.write
        else:
            self._write = (lambda x: stream.write(
                x.encode(self.encoding, 'replace')))
        self._write_object(self.obj, None)

    def _write_object(self, obj, parent):
        if obj.is_truth():
            self._write_truth(obj, parent)
        elif obj.is_falsity():
            self._write_falsity(obj, parent)
        elif obj.is_not():
            self._write_not(obj, parent)
        elif obj.is_and():
            self._write_and(obj, parent)
        elif obj.is_or():
            self._write_or(obj, parent)
        elif obj.is_implies():
            self._write_implies(obj, parent)
        elif obj.is_iff():
            self._write_iff(obj, parent)
        elif obj.is_equal():
            self._write_equal(obj, parent)
        elif obj.is_forall():
            self._write_forall(obj, parent)
        elif obj.is_exists():
            self._write_exists(obj, parent)
        elif obj.is_application():
            self._write_application(obj, parent)
        elif obj.is_variable():
            self._write_variable(obj, parent)
        elif obj.is_constant():
            self._write_constant(obj, parent)
        elif obj.is_new_axiom():
            self._write_new_axiom(obj, parent)
        elif obj.is_theory():
            self._write_theory(obj, parent)
        else:
            raise self.error(f"cannot serialize '{obj}'")

    def _write_objects_separated_by(self, sep, objs, parent):
        it = iter(objs)
        obj = next(it, None)
        if obj:
            self._write_object(obj, parent)
        for obj in it:
            self._write(sep)
            self._write_object(obj, parent)

    def _write_truth(self, obj, parent):
        self._write('$true')

    def _write_falsity(self, obj, parent):
        self._write('$false')

    def _write_not(self, obj, parent):
        self._write('~ ')
        self._write_object(obj[1], parent)

    def _write_and(self, obj, parent, symbol='&'):
        self._write('(')
        self._write_object(obj[0][1], obj)
        self._write(f' {symbol} ')
        self._write_object(obj[1], obj)
        self._write(')')

    def _write_or(self, obj, parent, symbol='|'):
        self._write_and(obj, parent, symbol)

    def _write_implies(self, obj, parent, symbol='=>'):
        self._write_and(obj, parent, symbol)

    def _write_iff(self, obj, parent, symbol='<=>'):
        self._write_and(obj, parent, symbol)

    def _write_equal(self, obj, parent, symbol='='):
        self._write_and(obj, parent, symbol)

    def _write_quantifier(self, vars, body, parent, symbol):
        self._write(f'( {symbol} [')
        self._write_objects_separated_by(',', vars, parent)
        self._write('] : ')
        self._write_object(body, parent)
        self._write(')')

    def _write_forall(self, obj, parent, symbol='!'):
        *vars, body = obj.unfold_forall()
        self._write_quantifier(vars, body, obj, symbol)

    def _write_exists(self, obj, parent, symbol='?'):
        *vars, body = obj.unfold_exists()
        self._write_quantifier(vars, body, obj, symbol)

    def _write_application(self, obj, parent):
        op, *args = obj.unfold_application()
        self._write_object(op, obj)
        self._write('(')
        self._write_objects_separated_by(',', args, obj)
        self._write(')')

    def _write_variable(self, obj, parent):
        self._write('V' + self._normalize_id(obj.id))

    def _write_constant(self, obj, parent):
        self._write('c' + self._normalize_id(obj.id))

    def _write_new_axiom(self, obj, parent):
        self._write_fof(self._normalize_id(obj[0].id), 'axiom', obj[1], obj)

    def _write_theory(self, obj, parent):
        it = filter(lambda x: x.is_new_axiom(), obj.args_no_prelude)
        self._write_objects_separated_by('\n', it, obj)

    def _write_fof(self, name, role, obj, parent):
        self._write('fof(')
        self._write(name)
        self._write(',')
        self._write(role)
        self._write(',')
        self._write_object(obj, parent)
        self._write(').')

    def _normalize_id(self, id, _re=re.compile('\W')):
        return _re.sub('_', str(id))
