# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from .serializer import Serializer, SerializerSettings

NONE = ('', '')
LSPACE = (' ', '')
RSPACE = ('', ' ')
LRSPACE = (' ', ' ')


class SerializerULKB_Settings(SerializerSettings):
    ensure_ascii = False
    omit_annotations = True
    omit_generated_ids = True
    omit_labels = False
    omit_parentheses = True
    omit_types = True

    show_annotations = property(
        lambda x: not x.omit_annotations,
        lambda x, v: setattr(x, 'omit_annotations', not v))

    show_generated_ids = property(
        lambda x: not x.omit_generated_ids,
        lambda x, v: setattr(x, 'omit_generated_ids', not v))

    show_labels = property(
        lambda x: not x.omit_labels,
        lambda x, v: setattr(x, 'omit_labels', not v))

    show_parentheses = property(
        lambda x: not x.omit_parentheses,
        lambda x, v: setattr(x, 'omit_parentheses', not v))

    show_types = property(
        lambda x: not x.omit_types,
        lambda x, v: setattr(x, 'omit_types', not v))

    lbrace = '('
    rbrace = ')'

    type_sort = '*'
    type_sort_spaces = NONE
    type_symbol = ':'
    type_symbol_spaces = LRSPACE

    bool_type_symbol = ('bool', '𝔹')
    bool_type_symbol_spaces = NONE

    function_type_symbol = ('->', '→')
    function_type_symbol_spaces = LRSPACE

    int_type_symbol = ('int', 'ℤ')
    int_type_symbol_spaces = NONE

    real_type_symbol = ('real', 'ℝ')
    real_type_symbol_spaces = NONE

    str_type_literal_lbrace = "'"
    str_type_literal_rbrace = "'"

    equal_symbol = '='
    equal_symbol_spaces = LRSPACE
    distinct_symbol = ('!=', '≠')
    distinct_symbol_spaces = LRSPACE

    ge_symbol = ('>=', '≥')
    ge_symbol_spaces = LRSPACE
    gt_symbol = '>'
    gt_symbol_spaces = LRSPACE
    le_symbol = ('<=', '≤')
    le_symbol_spaces = LRSPACE
    lt_symbol = '<'
    lt_symbol_spaces = LRSPACE

    truth_symbol = ('true', '⊤')
    truth_symbol_spaces = NONE
    falsity_symbol = ('false', '⊥')
    falsity_symbol_spaces = NONE
    not_symbol = ('not ', '¬')
    not_symbol_spaces = NONE
    and_symbol = ('and', '∧')
    and_symbol_spaces = LRSPACE
    or_symbol = ('or', '∨')
    or_symbol_spaces = LRSPACE
    implies_symbol = ('->', '→')
    implies_symbol_spaces = LRSPACE
    iff_symbol = ('<->', '↔')
    iff_symbol_spaces = LRSPACE

    exists_symbol = ('exists', '∃')
    exists_symbol_spaces = RSPACE
    exists_separator = ','
    exists_separator_spaces = RSPACE
    exists_variable_separator = ' '
    exists_variable_separator_spaces = NONE

    exists1_symbol = ('exists1', '∃!')
    exists1_symbol_spaces = RSPACE
    exists1_separator = ','
    exists1_separator_spaces = RSPACE
    exists1_variable_separator = ' '
    exists1_variable_separator_spaces = NONE

    forall_symbol = ('forall', '∀')
    forall_symbol_spaces = RSPACE
    forall_separator = ','
    forall_separator_spaces = RSPACE
    forall_variable_separator = ' '
    forall_variable_separator_spaces = NONE

    application_symbol = ' '
    application_symbol_spaces = NONE
    abstraction_symbol = ('fun', '𝜆')
    abstraction_symbol_spaces = RSPACE
    abstraction_separator = ('=>', '⇒')
    abstraction_separator_spaces = LRSPACE
    abstraction_variable_separator = ' '
    abstraction_variable_separator_spaces = NONE

    sequent_symbol = ('|-', '⊢')
    sequent_symbol_spaces = RSPACE
    sequent_hypothesis_separator = ','
    sequent_hypothesis_separator_spaces = RSPACE

    new_type_constructor_symbol = 'type_constructor'
    new_type_constructor_symbol_spaces = RSPACE
    new_type_constructor_arg_separator = ' '
    new_type_constructor_arg_separator_spaces = NONE

    new_constant_symbol = 'constant'
    new_constant_symbol_spaces = RSPACE

    new_axiom_symbol = 'axiom'
    new_axiom_symbol_spaces = RSPACE
    new_axiom_separator = (':=', '≔')
    new_axiom_separator_spaces = LRSPACE

    new_definition_symbol = 'definition'
    new_definition_symbol_spaces = RSPACE
    new_definition_separator = (':=', '≔')
    new_definition_separator_spaces = LRSPACE

    new_theorem_symbol = 'theorem'
    new_theorem_symbol_spaces = RSPACE
    new_theorem_separator = (':=', '≔')
    new_theorem_separator_spaces = LRSPACE

    new_python_type_alias_symbol = 'python_type_alias'
    new_python_type_alias_symbol_spaces = RSPACE
    new_python_type_alias_arg_separator = ' '
    new_python_type_alias_arg_separator_spaces = NONE

    theory_begin_symbol = 'begin theory'
    theory_begin_symbol_spaces = ('', '\n')
    theory_end_symbol = 'end theory'
    theory_end_symbol_spaces = NONE
    theory_extension_separator = ''
    theory_extension_separator_spaces = ('', '\n')

    label_lbrace = ('<', '‹')
    label_rbrace = ('>', '›')

    annotation_lbrace = '{'
    annotation_rbrace = '}'
    annotation_symbol = ' '
    annotation_symbol_spaces = NONE
    annotation_item_assignment = '='
    annotation_item_assignment_spaces = NONE
    annotation_item_separator = ','
    annotation_item_separator_spaces = RSPACE
    annotation_embedded_object_lbrace = ('<', '⟨')
    annotation_embedded_object_rbrace = ('>', '⟩')

    def _get_symbol(self, name):
        sym = getattr(self, name)
        if isinstance(sym, (tuple, list)):
            if self.ensure_ascii:
                return sym[0]   # ascii
            else:
                return sym[1]   # utf-8
        else:
            return sym

    def _get_symbol_with_spaces(self, name):
        lspace, rspace = getattr(self, name + '_spaces')
        return lspace + self._get_symbol(name) + rspace


class SerializerULKB(
        Serializer, format='ulkb', format_long='ULKB',
        settings=SerializerULKB_Settings):

    def __init__(self, obj, encoding=None, **kwargs):
        super().__init__(obj, encoding=encoding, **kwargs)
        self.settings = self.cls._thy().settings.serializer.ulkb(**kwargs)
        self.kwargs = kwargs
        self.ensure_ascii = self.settings.ensure_ascii
        self.show_annotations = self.settings.show_annotations
        self.show_generated_ids = self.settings.show_generated_ids
        self.show_labels = self.settings.show_labels
        self.show_parentheses = self.settings.show_parentheses
        self.show_types = self.settings.show_types
        self.lbrace = self.settings.lbrace
        self.rbrace = self.settings.rbrace
        self._get_symbol = self.settings._get_symbol
        self._get_symbol_with_spaces = self.settings._get_symbol_with_spaces

    def do_serialize_to_stream(self, stream):
        import io
        self.stream = stream
        if isinstance(stream, io.TextIOBase):
            self._write = stream.write
        else:
            self._write = (lambda x: stream.write(
                x.encode(self.encoding, 'replace')))
        self._write_object(self.obj, None)

    def _do_serialize_to_stream(self, obj, omit_type_sort=True):
        serializer = self.__class__(obj, **self.kwargs)
        serializer._omit_type_sort = omit_type_sort
        serializer.do_serialize_to_stream(self.stream)

    def _write_object(self, obj, parent):
        if (obj.is_type_constructor() or obj.is_type_variable()
                or obj.is_atomic_term()):
            self._write_atomic_term(obj, parent)
        elif obj.is_base_type():
            if obj.is_bool_type():
                self._write_bool_type(obj, parent)
            elif obj.is_int_type():
                self._write_int_type(obj, parent)
            elif obj.is_real_type():
                self._write_real_type(obj, parent)
            else:
                self._write_base_type(obj, parent)
        elif obj.is_function_type():
            self._write_function_type(obj, parent)
        elif obj.is_type_application():
            self._write_type_application(obj, parent)
        elif obj.is_equal() and not obj.is_iff():
            self._write_equal(obj, parent)
        elif obj.is_not():
            (arg0,) = obj.unpack_not()
            if (arg0.is_equal()
                and not arg0.is_iff()
                and not self.show_parentheses
                and (parent is None
                     or not self._should_write_type(obj, parent))
                and not self._should_write_annotations(obj)
                    and not self._should_write_annotations(obj[1])):
                self._write_distinct(obj, parent)
            else:
                self._write_not(obj, parent)
        elif obj.is_and():
            self._write_and(obj, parent)
        elif obj.is_or():
            self._write_or(obj, parent)
        elif obj.is_implies():
            self._write_implies(obj, parent)
        elif obj.is_iff():
            self._write_iff(obj, parent)
        elif obj.is_exists() and obj[1].is_abstraction():
            self._write_exists(obj, parent)
        elif obj.is_exists1() and obj[1].is_abstraction():
            self._write_exists1(obj, parent)
        elif obj.is_forall() and obj[1].is_abstraction():
            self._write_forall(obj, parent)
        elif obj.is_application():
            if obj[0].is_application():  # FIXME: generalize
                f = obj[0][0]
                if f == self.cls.IntType.ge or f == self.cls.RealType.ge:
                    self._write_ge(obj, parent)
                elif f == self.cls.IntType.gt or f == self.cls.RealType.gt:
                    self._write_gt(obj, parent)
                elif f == self.cls.IntType.le or f == self.cls.RealType.le:
                    self._write_le(obj, parent)
                elif f == self.cls.IntType.lt or f == self.cls.RealType.lt:
                    self._write_lt(obj, parent)
                else:
                    self._write_application(obj, parent)
            else:
                self._write_application(obj, parent)
        elif obj.is_abstraction():
            self._write_abstraction(obj, parent)
        elif obj.is_sequent():
            self._write_sequent(obj, parent)
        elif obj.is_new_type_constructor():
            self._write_new_type_constructor(obj, parent)
        elif obj.is_new_constant():
            self._write_new_constant(obj, parent)
        elif obj.is_new_axiom():
            self._write_new_axiom(obj, parent)
        elif obj.is_new_definition():
            self._write_new_definition(obj, parent)
        elif obj.is_new_theorem():
            self._write_new_theorem(obj, parent)
        elif obj.is_new_python_type_alias():
            self._write_new_python_type_alias(obj, parent)
        elif obj.is_theory():
            self._write_theory(obj, parent)
        else:
            self._write(obj.dump())  # fallback to raw serialization

    def _write_atomic_term(self, obj, parent):
        if obj.is_truth():
            self._write_symbol_with_spaces('truth_symbol')
        elif obj.is_falsity():
            self._write_symbol_with_spaces('falsity_symbol')
        elif (obj.is_constant()
              and obj.type.is_str_type()
              and isinstance(obj.id, str)):
            self._write_symbol('str_type_literal_lbrace')
            self._write_ensuring_ascii(obj.id.replace("'", "\\'"))
            self._write_symbol('str_type_literal_rbrace')
        else:
            self._write_id(obj)
        self._write_annotations_and_type(obj, parent)

    def _write_bool_type(self, obj, parent, symbol='bool_type_symbol'):
        self._write_symbol_with_spaces(symbol)
        self._write_annotations_and_type(obj, parent)

    def _write_int_type(self, obj, parent):
        self._write_bool_type(obj, parent, 'int_type_symbol')

    def _write_real_type(self, obj, parent):
        self._write_bool_type(obj, parent, 'real_type_symbol')

    def _write_base_type(self, obj, parent):
        self._write_arg(0, obj[0], obj[0], obj)
        self._write_annotations_and_type(obj, parent)

    def _write_function_type(self, obj, parent):
        self._write_arg(0, obj[1], obj, parent, self.cls.test_function_type)
        self._write_symbol_with_spaces('function_type_symbol')
        self._write_arg(1, obj[2], obj, parent, self.cls.test_function_type)
        self._write_annotations_and_type(obj, parent)

    def _write_type_application(self, obj, parent):
        self._write_arg(0, obj[0], obj, parent)
        for i, arg in enumerate(obj.tail):
            self._write_symbol_with_spaces('application_symbol')
            self._write_arg(
                i, arg, obj, parent, lambda x:
                obj.test(x) and x.head == obj.head)
        self._write_annotations_and_type(obj, parent)

    def _write_equal(self, obj, parent):
        self._write_arg(0, obj[0][1], obj, parent, self.cls.test_equal)
        self._write_symbol_with_spaces('equal_symbol')
        self._write_arg(1, obj[1], obj, parent, self.cls.test_equal)
        self._write_annotations_and_type(obj, parent)

    def _write_distinct(self, obj, parent):
        self._write_arg(0, obj[1][0][1], obj, parent, self.cls.test_equal)
        self._write_symbol_with_spaces('distinct_symbol')
        self._write_arg(1, obj[1][1], obj, parent, self.cls.test_equal)
        self._write_annotations_and_type(obj, parent)

    def _write_ge(self, obj, parent, symbol='ge_symbol'):
        self._write_arg(0, obj[0][1], obj, parent)
        self._write_symbol_with_spaces(symbol)
        self._write_arg(1, obj[1], obj, parent)
        self._write_annotations_and_type(obj, parent)

    def _write_gt(self, obj, parent, symbol='gt_symbol'):
        self._write_ge(obj, parent, symbol)

    def _write_le(self, obj, parent, symbol='le_symbol'):
        self._write_ge(obj, parent, symbol)

    def _write_lt(self, obj, parent, symbol='lt_symbol'):
        self._write_ge(obj, parent, symbol)

    def _write_not(self, obj, parent):
        self._write_symbol_with_spaces('not_symbol')
        self._write_arg(1, obj[1], obj, parent, self.cls.test_not)
        self._write_annotations_and_type(obj, parent)

    def _write_and(self, obj, parent, symbol='and_symbol', test=None):
        test = test or self.cls.test_and
        self._write_arg(0, obj[0][1], obj, parent, test)
        self._write_symbol_with_spaces(symbol)
        self._write_arg(1, obj[1], obj, parent, test)
        self._write_annotations_and_type(obj, parent)

    def _write_or(self, obj, parent):
        self._write_and(
            obj, parent, symbol='or_symbol', test=self.cls.test_or)

    def _write_implies(self, obj, parent):
        self._write_and(
            obj, parent, symbol='implies_symbol',
            test=self.cls.test_implies)

    def _write_iff(self, obj, parent):
        self._write_and(
            obj, parent, symbol='iff_symbol', test=self.cls.test_iff)

    def _write_exists(
            self, obj, parent, symbol='exists_symbol',
            separator='exists_separator',
            variable_separator='exists_variable_separator', test=None):
        test = test or self.cls.test_exists
        parenthesize = self._should_write_annotations_or_type(obj, parent)
        if parenthesize:
            self._write_lbrace()
        if (not parent or not test(parent)
                or parenthesize or self.show_parentheses):
            self._write_symbol_with_spaces(symbol)
        arg0, arg1 = obj[1].unpack_abstraction()
        if (not test(arg1) or self._should_parenthesize_arg(
                1, arg1, arg1, obj, test)):
            self._write_arg(0, arg0, obj, obj, test)
            self._write_symbol_with_spaces(separator)
            self._write_arg(1, arg1, obj, obj, test)
        else:
            self._write_arg(0, arg0, obj, obj, test)
            self._write_symbol_with_spaces(variable_separator)
            self._write_arg(1, arg1, obj, obj, test)
        if parenthesize:
            self._write_rbrace()
        self._write_annotations_and_type(obj, parent)

    def _write_exists1(self, obj, parent):
        self._write_exists(
            obj, parent, symbol='exists1_symbol',
            separator='exists1_separator',
            variable_separator='exists1_variable_separator',
            test=self.cls.test_exists1)

    def _write_forall(self, obj, parent):
        self._write_exists(
            obj, parent, symbol='forall_symbol',
            separator='forall_separator',
            variable_separator='forall_variable_separator',
            test=self.cls.test_forall)

    def _write_application(self, obj, parent):
        self._write_arg(0, obj[0], obj, parent)
        for i in range(1, len(obj.args)):
            self._write_symbol_with_spaces('application_symbol')
            self._write_arg(i, obj[i], obj, parent)
        self._write_annotations_and_type(obj, parent)

    def _write_abstraction(self, obj, parent):
        test = self.cls.test_abstraction
        parenthesize = self._should_write_annotations_or_type(obj, parent)
        if parenthesize:
            self._write_lbrace()
        if (not parent or not test(parent)
                or parenthesize or self.show_parentheses):
            self._write_symbol_with_spaces('abstraction_symbol')
        arg0, arg1 = obj.unpack_abstraction()
        if (not test(arg1) or self._should_parenthesize_arg(
                1, arg1, obj, parent, test)):
            self._write_arg(0, arg0, obj, parent, test)
            self._write_symbol_with_spaces('abstraction_separator')
            self._write_arg(1, arg1, obj, parent, test)
        else:
            self._write_arg(0, arg0, obj, parent, test)
            self._write_symbol_with_spaces('abstraction_variable_separator')
            self._write_arg(1, arg1, obj, parent, test)
        if parenthesize:
            self._write_rbrace()
        self._write_annotations_and_type(obj, parent)

    def _write_sequent(self, obj, parent):
        for i, arg in enumerate(obj.hypotheses):
            self._write_arg(i, arg, obj, parent)
            if i < len(obj.hypotheses) - 1:
                self._write_symbol_with_spaces(
                    'sequent_hypothesis_separator')
            else:
                self._write(' ')
        self._write_symbol_with_spaces('sequent_symbol')
        self._write_arg(len(obj.hypotheses), obj.conclusion, obj, parent)
        self._write_annotations_and_type(obj, parent)

    def _write_new_type_constructor(self, obj, parent):
        self._write_symbol_with_spaces('new_type_constructor_symbol')
        (arg0,) = obj.unpack_new_type_constructor()
        self._write_arg(0, arg0, obj, parent)
        self._write_symbol_with_spaces('new_type_constructor_arg_separator')
        self._write(str(arg0.arity))
        if arg0.arity == 2 and arg0.associativity:
            self._write_symbol_with_spaces(
                'new_type_constructor_arg_separator')
            self._write(arg0.associativity)
        self._write_annotations(obj)

    def _write_new_constant(self, obj, parent):
        self._write_symbol_with_spaces('new_constant_symbol')
        (arg0,) = obj.unpack_new_constant()
        self._write_arg(0, arg0, obj, parent)
        self._write_annotations(obj)

    def _write_new_axiom(self, obj, parent):
        self._write_symbol_with_spaces('new_axiom_symbol')
        (arg0, arg1) = obj.unpack_new_axiom()
        show_id = (
            self.show_generated_ids or not obj._is_generated_id(obj.id))
        if show_id:
            self._write_arg(0, arg0, obj, parent)
        self._write_annotations(obj)
        if show_id:
            self._write_symbol_with_spaces('new_axiom_separator')
        self._write_arg(1, arg1, obj, parent)

    def _write_new_definition(self, obj, parent):
        self._write_symbol_with_spaces('new_definition_symbol')
        (arg0,) = obj.unpack_new_definition()
        self._write_arg(0, arg0[0][1], obj, parent)
        self._write_annotations(obj)
        self._write_symbol_with_spaces('new_definition_separator')
        self._write_arg(1, arg0[1], obj, parent)

    def _write_new_theorem(self, obj, parent):
        self._write_symbol_with_spaces('new_theorem_symbol')
        (arg0, arg1) = obj.unpack_new_theorem()
        show_id = (
            self.show_generated_ids or not obj._is_generated_id(obj.id))
        if show_id:
            self._write_arg(0, arg0, obj, parent)
        self._write_annotations(obj)
        if show_id:
            self._write_symbol_with_spaces('new_theorem_separator')
        self._write_arg(1, arg1[1], obj, parent)

    def _write_new_python_type_alias(self, obj, parent):
        self._write_symbol_with_spaces('new_python_type_alias_symbol')
        arg0, arg1, arg2 = obj.unpack_new_python_type_alias()
        self._write(str(arg0.__name__))
        self._write_symbol_with_spaces(
            'new_python_type_alias_arg_separator')
        self._write_arg(1, arg1, obj, parent)
        if arg2:
            self._write_symbol_with_spaces(
                'new_python_type_alias_arg_separator')
            self._write(arg2)
        self._write_annotations(obj)

    def _write_theory(self, obj, parent):
        self._write_symbol_with_spaces('theory_begin_symbol')
        for i, arg in enumerate(obj.args):
            self._write_arg(i, arg, obj, parent)
            self._write_symbol_with_spaces('theory_extension_separator')
        self._write_symbol_with_spaces('theory_end_symbol')
        self._write_annotations(obj)

    def _write_annotations_and_type(self, obj, parent):
        self._write_annotations(obj)
        self._write_type(obj, parent)

    def _write_annotations(self, obj):
        if self._should_write_annotations(obj):
            self._write_symbol_with_spaces('annotation_symbol')
            self._write_annotations_tail(obj.annotations)

    def _write_annotations_tail(self, annotations):
        self._write_symbol('annotation_lbrace')
        for i, (k, v) in enumerate(annotations.items()):
            self._write(k)
            self._write_symbol_with_spaces('annotation_item_assignment')
            self._write_annotation_value(v)
            if i < len(annotations) - 1:
                self._write_symbol_with_spaces('annotation_item_separator')
        self._write_symbol('annotation_rbrace')

    def _write_annotation_value(self, v):
        if isinstance(v, dict):
            self._write('{')
            t, sep = v, 'annotation_item_separator'
            for i, (k, v) in enumerate(t.items()):
                self._write_annotation_value(k)
                self._write(': ')
                self._write_annotation_value(v)
                if i < len(t) - 1:
                    self._write_symbol_with_spaces(sep)
            self._write('}')
        elif isinstance(v, (tuple, list, set)):
            if isinstance(v, tuple):
                lbrace, rbrace = '(', ')'
            elif isinstance(v, list):
                lbrace, rbrace = '[', ']'
            else:
                lbrace, rbrace = '{', '}'
            self._write(lbrace)
            for i, x in enumerate(v):
                self._write_annotation_value(x)
                if i < len(v) - 1:
                    self._write(', ')
            if isinstance(v, tuple) and len(v) == 1:
                self._write(',')
            self._write(rbrace)
        elif self.cls.Object.test(v):
            self._write_symbol('annotation_embedded_object_lbrace')
            self._do_serialize_to_stream(v, omit_type_sort=False)
            self._write_symbol('annotation_embedded_object_rbrace')
        elif isinstance(v, str):
            self._write("'")
            self._write_ensuring_ascii(v.replace("'", "\\'"))
            self._write("'")
        else:
            self._write(str(v))

    def _write_type(self, obj, parent):
        if self._should_write_type(obj, parent):
            self._write_symbol_with_spaces('type_symbol')
            if obj.is_type():
                self._write_symbol_with_spaces('type_sort')
            else:
                self._do_serialize_to_stream(obj.type)

    def _write_arg(self, i, arg, obj, parent, test=None):
        if self._should_parenthesize_arg(i, arg, obj, parent, test):
            self._write_lbrace()
            self._write_object(arg, obj)
            self._write_rbrace()
        else:
            self._write_object(arg, obj)

    def _write_id(self, obj):
        if self.show_labels and 'label' in obj.annotations:
            self._write_symbol('label_lbrace')
            self._write_ensuring_ascii(obj.annotations['label'])
            self._write_symbol('label_rbrace')
        else:
            self._write_ensuring_ascii(str(obj.id))

    def _write_symbol(self, symbol_name):
        self._write(self._get_symbol(symbol_name))

    def _write_symbol_with_spaces(self, symbol_name):
        self._write(self._get_symbol_with_spaces(symbol_name))

    def _write_lbrace(self):
        self._write(self.lbrace)

    def _write_rbrace(self):
        self._write(self.rbrace)

    def _write_ensuring_ascii(self, text):
        if self.ensure_ascii:
            self._write(text.encode(
                'ascii', 'backslashreplace').decode('ascii'))
        else:
            self._write(text)

    def _should_write_annotations(self, obj):
        return self.show_annotations and obj.annotations

    def _should_write_annotations_or_type(self, obj, parent):
        return (self._should_write_annotations(obj)
                or self._should_write_type(obj, parent))

    def _should_write_type(self, obj, parent):
        if obj.is_atomic_term():
            return self.show_types or parent is None or (
                parent
                and parent.is_extension()
                and not parent.is_new_axiom()
                and not parent.is_new_theorem())
            # return self.show_types
        elif obj.is_term():
            return parent is None
        elif obj.is_type():
            if parent:
                return not parent.is_type()
            else:
                return (not hasattr(self, '_omit_type_sort')
                        or not self._omit_type_sort)
        else:
            return False

    def _should_parenthesize_arg(self, i, arg, obj, parent, test=None):
        if arg.is_theory() or arg.is_extension():
            return False
        if (self._should_write_type(arg, obj)
                or self._should_write_annotations(arg)):
            return True
        if self._get_precedence(arg) > self._get_precedence(obj):
            return True
        if (test or obj.test)(arg):
            if obj.is_not():
                return False
            elif self._is_right_associative(obj):
                return (i == 1 and self.show_parentheses) or i == 0
            elif self._is_left_associative(obj):
                return (i == 0 and self.show_parentheses) or i == 1
            elif arg.is_type_application():
                return True     # nested type applications
        if self._is_compound(arg):
            return self.show_parentheses
        return False

    def _get_precedence(self, obj):
        if (obj.is_type_constructor() or obj.is_type_variable()
                or obj.is_base_type() or obj.is_atomic_term()):
            return 0
        elif obj.is_not():
            return 75
        elif obj.is_and():
            return 80
        elif obj.is_or():
            return 85
        elif obj.is_implies():
            return 90
        elif obj.is_iff():
            return 95
        elif obj.is_equal():
            return 70
        elif obj.is_exists() or obj.is_exists1() or obj.is_forall():
            return 100
        elif obj.is_application():
            return 40
        elif obj.is_abstraction():
            return 100
        elif obj.is_type_application() and not obj.is_function_type():
            return 100
        else:
            return 200

    def _is_left_associative(self, obj):
        return obj.is_application()

    def _is_right_associative(self, obj):
        return (obj.is_function_type() or obj.is_abstraction()
                or obj.is_and() or obj.is_or() or obj.is_implies()
                or obj.is_iff() or obj.is_exists() or obj.is_exists1()
                or obj.is_forall())

    def _is_compound(self, obj):
        return (obj.is_compound_term()
                or (obj.is_type_application() and len(obj.args) > 1))
