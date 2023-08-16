# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestCommands(ULKB_TestCase):

    # -- Adding extensions -------------------------------------------------

    def test_extend(self):
        ext = NewConstant(Constant('a', BoolType()))
        thy = Theory.push(Theory())
        ret = extend(ext)
        self.assert_deep_equal(ret, ext)
        self.assert_deep_equal(thy[-1], ext)
        self.assertEqual(len(thy.args_no_prelude), 1)
        self.assertEqual(len(Theory.top.args_no_prelude), 1)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

    def test_new_base_type(self):
        thy = Theory.push(Theory())
        ret = new_base_type('T', x=1, y=2)
        self.assert_base_type(ret, (TypeConstructor('T', 0),))
        ext = thy[-1]
        self.assert_new_type_constructor(
            ext, (TypeConstructor('T', 0),))
        self.assert_type_constructor(
            ext[0], ('T', 0, None), {'x': 1, 'y': 2})
        self.assertEqual(len(Theory.top.args_no_prelude), 1)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

    def test_new_type_constructor(self):
        thy = Theory.push(Theory())
        ret = new_type_constructor('T', 5, 'left', x=1, y=2)
        self.assert_type_constructor(
            ret, ('T', 5, 'left'), {'x': 1, 'y': 2})
        ext = thy[-1]
        self.assert_new_type_constructor(
            ext, (TypeConstructor('T', 5, 'left'),))
        self.assert_type_constructor(
            ext[0], ('T', 5, 'left'), {'x': 1, 'y': 2})
        self.assertEqual(len(Theory.top.args_no_prelude), 1)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

    def test_new_constant(self):
        thy = Theory.push(Theory())
        ret = new_constant('c', bool, x=1, y=2)
        self.assert_constant(ret, ('c', BoolType(),), {'x': 1, 'y': 2})
        ext = thy[-1]
        self.assert_new_constant(
            ext, (Constant('c', BoolType()),))
        self.assert_constant(
            ext[0], ('c', BoolType()), {'x': 1, 'y': 2})
        self.assertEqual(len(Theory.top.args_no_prelude), 1)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

    def test_new_axiom(self):
        thy = Theory.push(Theory())
        ret = new_axiom('f', Falsity(), x=1, y=2)
        self.assert_sequent(ret, (frozenset(), Falsity()))
        ext = thy[-1]
        self.assert_new_axiom(
            ext, (Constant('f', BoolType()), Falsity()),
            {'x': 1, 'y': 2})
        self.assertEqual(len(Theory.top.args_no_prelude), 1)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

        # generate id
        thy = Theory.push(Theory())
        ret = new_axiom(Falsity(), x=1, y=2)
        self.assert_sequent(ret, (frozenset(), Falsity()))
        ext = thy[-1]
        self.assertEqual(ext.id, Falsity()._as_id())
        Theory.pop()

    def test_new_definition(self):
        thy = Theory.push(Theory())
        ret = new_definition('x', Truth(), x=1, y=2)
        self.assert_constant(ret, ('x', BoolType()))
        ext = thy[-1]
        self.assert_new_definition(
            ext, (Equal(Variable('x', BoolType()), Truth()),),
            {'x': 1, 'y': 2})
        self.assertEqual(len(Theory.top.args_no_prelude), 1)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

    def test_new_theorem(self):
        thy = Theory.push(Theory())
        seq = new_axiom('ax', Falsity())
        ret = new_theorem('thm', seq, x=1, y=2)
        self.assert_sequent(ret, (frozenset(), Falsity()))
        ext = thy[-1]
        self.assert_new_theorem(
            ext, (Constant('thm', BoolType()), seq), {'x': 1, 'y': 2})
        self.assertEqual(len(Theory.top.args_no_prelude), 2)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

        # generate id
        thy = Theory.push(Theory())
        seq = new_axiom('ax', Falsity())
        ret = new_theorem(seq, x=1, y=2)
        self.assert_sequent(ret, (frozenset(), Falsity()))
        ext = thy[-1]
        self.assertEqual(ext.id, seq._as_id())
        Theory.pop()

    def test_new_python_type_alias(self):
        thy = Theory.push(Theory())
        INT = new_base_type('INT')
        ret = new_python_type_alias(int, INT, x=1, y=2)
        self.assert_base_type(ret, (INT[0],))
        ext = thy[-1]
        self.assert_new_python_type_alias(
            ext, (int, INT, None), {'x': 1, 'y': 2})
        self.assertEqual(len(Theory.top.args_no_prelude), 2)
        Theory.pop()
        self.assertEqual(len(Theory.top.args_no_prelude), 0)

    # -- Removing extensions -----------------------------------------------

    def test_reset_error(self):
        thy = Theory.push(Theory())
        self.assertRaisesRegex(LookupError, 'no such extension', reset, thy)
        Theory.pop()

    def test_reset_none(self):
        thy = Theory.push(Theory())
        self.assertEqual(reset(), 0)
        Theory.pop()
        self.assertEqual(len(thy), len(Theory()))
        self.assertEqual(thy.hexdigest, Theory().hexdigest)

    def test_reset_nonneg(self):
        thy = Theory.push(Theory())
        saved_len = len(thy)
        self.assertEqual(reset(0), saved_len)
        Theory.pop()
        self.assertEqual(len(thy), 0)
        self.assertEqual(thy.prelude_offset, 0)
        self.assertEqual(thy.hexdigest, EmptyTheory().hexdigest)
        self.assertEqual(thy.ids, dict())
        self.assertEqual(thy.type_constructors, set())
        self.assertEqual(thy.type_constructors_dict, dict())
        self.assertEqual(thy.constants, set())
        self.assertEqual(thy.constants_dict, dict())
        self.assertEqual(thy.axioms_dict, dict())
        self.assertEqual(thy.definitions_dict, dict())
        self.assertEqual(thy.theorems_dict, dict())
        self.assertEqual(thy.python_type_aliases_dict, dict())

    def test_reset_neg(self):
        thy = Theory.push(Theory())
        new_axiom(Truth())
        new_axiom(Falsity())
        new_axiom(Truth())      # duplicated, should be ignored
        new_axiom(Not(Truth()))
        self.assertEqual(len(thy.args_no_prelude), 3)
        self.assertEqual(reset(-1), 1)
        self.assertEqual(
            thy.args[-1],
            NewAxiom(Constant(Falsity()._as_id(), bool), Falsity()))
        self.assertEqual(reset(-2), 2)
        self.assertEqual(thy.args_no_prelude, [])
        Theory.pop()
        self.assertEqual(thy, _thy())
        self.assertEqual(thy.hexdigest, _thy().hexdigest)
        self.assertEqual(thy.ids, _thy().ids)
        self.assertEqual(thy.type_constructors, _thy().type_constructors)
        self.assertEqual(
            thy.type_constructors_dict, _thy().type_constructors_dict)
        self.assertEqual(thy.constants, _thy().constants)
        self.assertEqual(thy.constants_dict, _thy().constants_dict)
        self.assertEqual(thy.axioms_dict, _thy().axioms_dict)
        self.assertEqual(thy.definitions_dict, _thy().definitions_dict)
        self.assertEqual(thy.theorems_dict, _thy().theorems_dict)
        self.assertEqual(
            thy.python_type_aliases_dict, _thy().python_type_aliases_dict)

    def test_reset_id(self):
        thy = Theory.push(Theory())
        saved_len = len(thy)
        self.assertEqual(reset('bool'), saved_len)
        self.assertEqual(len(thy), 0)
        Theory.pop()

    def test_reset_extension(self):
        thy = Theory.push(Theory())
        new_theorem(new_axiom(Truth()))
        self.assertEqual(len(thy.args_no_prelude), 2)
        self.assertEqual(reset(thy[-2]), 2)
        Theory.pop()

    def test_reset_type_constructor(self):
        thy = Theory.push(Theory())
        tc1 = new_type_constructor('tc1', 0)
        tc2 = new_type_constructor('tc2', 0)
        tc3 = new_type_constructor('tc3', 0)
        self.assertEqual(reset(tc2), 2)
        self.assertEqual(thy[-1], NewTypeConstructor(tc1))
        Theory.pop()

    def test_reset_constant(self):
        thy = Theory.push(Theory())
        c1 = new_constant('c1', bool)
        c2 = new_constant('c2', bool)
        c3 = new_constant('c3', bool)
        self.assertEqual(reset(c2), 2)
        self.assertEqual(thy[-1], NewConstant(c1))
        Theory.pop()

    def test_reset_axiom(self):
        thy = Theory.push(Theory())
        ax1 = new_axiom('ax1', Truth())
        ax2 = new_axiom('ax2', Falsity())
        ax3 = new_axiom(Falsity())
        self.assertEqual(reset(lookup_extension('ax2')), 2)
        self.assertEqual(
            thy[-1], NewAxiom(Constant('ax1', bool), ax1[1]))
        Theory.pop()

    def test_reset_definition(self):
        thy = Theory.push(Theory())
        d1 = new_definition('d1', Truth())
        d2 = new_definition('d2', Falsity())
        d3 = new_definition('d3', Falsity())
        self.assertEqual(reset(lookup_extension('d2')), 2)
        self.assertEqual(
            thy[-1], NewDefinition(Equal(Variable(d1.id, bool), Truth())))
        Theory.pop()

    def test_reset_theorem(self):
        thy = Theory.push(Theory())
        seq = new_axiom(Truth())
        thm = new_theorem('t', seq)
        c = new_constant('c', int)
        self.assertEqual(reset(lookup_extension('t')), 2)
        self.assertEqual(
            thy[-1], NewAxiom(Constant(Truth()._as_id(), bool), Truth()))
        Theory.pop()

    def test_reset_python_type_alias(self):
        thy = Theory.push(Theory())
        saved_len = len(thy)
        self.assertEqual(
            reset(NewPythonTypeAlias(bool, BoolType(), 'BoolType')),
            saved_len - 1)
        Theory.pop()

    # -- Querying extensions -----------------------------------------------

    def test_enumerate_extensions(self):
        # error: cls is not a type
        Theory.push(EmptyTheory())
        self.assertRaisesRegex(
            TypeError, 'bad argument', list,
            enumerate_extensions(class_=0))
        Theory.pop()

        # error: arg is not an expression
        Theory.push(EmptyTheory())
        self.assertRaisesRegex(
            TypeError, 'bad argument', list,
            enumerate_extensions(lambda: 0))
        self.assertRaisesRegex(
            TypeError, 'bad argument', list,
            enumerate_extensions(Exception))
        Theory.pop()

        # empty prelude
        Theory.push(EmptyTheory())
        self.assertFalse(bool(list(enumerate_extensions())))
        Theory.pop()

        # empty non-prelude
        Theory.push(EmptyTheory())
        self.assertFalse(bool(list(enumerate_extensions())))
        Theory.pop()

        # empty theory
        Theory.push(EmptyTheory())
        tc1 = new_type_constructor('tc1', 0, i=1, j=2)
        exts = list(enumerate_extensions())
        self.assertEqual(len(exts), 1)
        i, ext = exts[0]
        self.assertEqual(i, 0)
        self.assert_new_type_constructor(ext, (tc1,))

        tc2 = new_type_constructor('tc2', 0, i=1, j=2)
        exts = list(enumerate_extensions())
        self.assertEqual(len(exts), 2)
        i, ext = exts[1]
        self.assertEqual(i, 1)
        self.assert_new_type_constructor(ext, (tc2,))

        k1 = new_constant('k1', tc1(), i=2, j=3)
        exts = list(enumerate_extensions())
        self.assertEqual(len(exts), 3)
        i, ext = exts[2]
        self.assertEqual(i, 2)
        self.assert_new_constant(ext, (k1,))

        k2 = new_constant('k2', tc2(), i=2, j=3)
        exts = list(enumerate_extensions())
        self.assertEqual(len(exts), 4)
        i, ext = exts[3]
        self.assertEqual(i, 3)
        self.assert_new_constant(ext, (k2,))

        # match tc1
        self.assertEqual(
            list(enumerate_extensions(tc1)), [exts[0], exts[2]])

        # match tc2
        self.assertEqual(
            list(enumerate_extensions(tc2)), [exts[1], exts[3]])

        # match k1
        self.assertEqual(list(enumerate_extensions(k1)), [exts[2]])

        # match k2
        self.assertEqual(list(enumerate_extensions(k2)), [exts[3]])

        # match id
        self.assertEqual(
            list(enumerate_extensions(id='tc1')), [exts[0]])
        self.assertEqual(
            list(enumerate_extensions(id='tc')), [exts[0], exts[1]])
        self.assertEqual(
            list(enumerate_extensions(id='k2')), [exts[3]])
        self.assertEqual(
            list(enumerate_extensions(id='k')), [exts[2], exts[3]])
        self.assertEqual(list(enumerate_extensions(id='^$')), [])
        self.assertEqual(list(enumerate_extensions(id='.')), exts)

        # match class
        self.assertEqual(
            list(enumerate_extensions(class_=NewTypeConstructor)),
            [exts[0], exts[1]])
        self.assertEqual(
            list(enumerate_extensions(class_=NewConstant)),
            [exts[2], exts[3]])
        self.assertEqual(
            list(enumerate_extensions(class_=Extension)), exts)
        self.assertEqual(
            list(enumerate_extensions(class_=NewAxiom)), [])

        # offset
        self.assertEqual(
            list(enumerate_extensions(offset=10)), exts[10:])
        self.assertEqual(
            list(enumerate_extensions(offset=2)), exts[2:])

        # limit
        self.assertEqual(
            list(enumerate_extensions(limit=1)), [exts[0]])
        self.assertEqual(
            list(enumerate_extensions(limit=0)), [])
        self.assertEqual(
            list(enumerate_extensions(limit=-1)), [])
        Theory.pop()

        # ordinary theory
        thy = Theory.push(Theory())
        self.assertEqual(
            next(enumerate_extensions(bool, offset=0, theory=thy)),
            (0, NewTypeConstructor(BoolType.constructor)))
        Theory.pop()

    def test_lookup_extension(self):
        Theory.push(EmptyTheory())

        # error: no such extension
        self.assertRaisesRegex(
            LookupError, 'no such extension',
            lookup_extension, 'tc')

        tc = new_type_constructor('tc', 0, i=1, j=2)
        self.assert_extension(lookup_extension('tc'), (tc,))
        Theory.pop()

    def test_lookup_type_constructor(self):
        Theory.push(EmptyTheory())

        # error: no such type constructor
        self.assertRaisesRegex(
            LookupError, 'no such type constructor',
            lookup_type_constructor, 'tc')

        tc = new_type_constructor('tc', 0, i=1, j=2)
        self.assertIs(lookup_type_constructor('tc'), tc)
        self.assertIs(lookup_type_constructor(tc), tc)

        Theory.pop()

    def test_lookup_constant(self):
        Theory.push(EmptyTheory())
        tc = new_type_constructor('tc', 0)
        self.assertRaisesRegex(
            LookupError, 'no such constant',
            lookup_constant, 'c')

        c = new_constant('c', tc(), i=1, j=2)
        self.assertIs(lookup_constant('c'), c)
        self.assertIs(lookup_constant(c), c)
        Theory.pop()

    def test_lookup_axiom(self):
        Theory.push(Theory())
        self.assertRaisesRegex(
            LookupError, 'no such axiom', lookup_axiom, 'ax')

        seq = new_axiom('ax', Truth(), i=1, j=2)
        self.assert_sequent(
            lookup_axiom('ax'), seq.args, seq.annotations)

        seq = new_axiom('ax', Truth(), i=1, j=2)
        self.assert_sequent(
            lookup_axiom(Constant('ax', bool)),
            seq.args, seq.annotations)

        seq = new_axiom(Falsity(), i=1, j=2)
        self.assert_sequent(
            lookup_axiom(Falsity()._as_id()), seq.args, seq.annotations)
        Theory.pop()

    def test_lookup_definition(self):
        Theory.push(Theory())
        self.assertRaisesRegex(
            LookupError, 'no such definition', lookup_definition, 't')

        t = new_definition('t', Truth(), i=1, j=2)
        self.assert_sequent(
            lookup_definition('t'), (frozenset(), Equal(t, Truth())))
        Theory.pop()

    def test_lookup_theorem(self):
        Theory.push(Theory())
        self.assertRaisesRegex(
            LookupError, 'no such theorem', lookup_theorem, 'thm')

        thm = new_theorem('thm', new_axiom(Truth()), i=1, j=2)
        self.assert_sequent(
            lookup_theorem('thm'), thm.args, thm.annotations)

        self.assert_sequent(
            lookup_theorem(Constant('thm', bool)),
            thm.args, thm.annotations)

        seq = new_theorem(new_axiom(Falsity()), i=1, j=2)
        self.assert_sequent(
            lookup_theorem(seq._as_id()), seq.args, seq.annotations)
        Theory.pop()

    def test_lookup_python_type_alias(self):
        thy = Theory.push(Theory())
        self.assertRaisesRegex(
            LookupError, 'no such type alias',
            lookup_python_type_alias, list)

        ty = lookup_python_type_alias(bool)
        self.assert_type_application(
            ty, (thy.BoolType.constructor,), (thy.BoolType.constructor,))
        Theory.pop()


if __name__ == '__main__':
    main()
