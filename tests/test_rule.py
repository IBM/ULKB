# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestRule(ULKB_TestCase):

    def test_rule_assume(self):
        self.assertRaises(TypeError, RuleAssume, 0)
        self.assertRaises(TypeError, RuleAssume, TypeVariable('a'))
        self.assertRaises(
            TypeError, RuleAssume, Constant('x', FunctionType(bool, bool)))

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        f = Constant('f', a >> a)
        g = Constant('g', type=(a, b) >> a)

        seq = RuleAssume(x@bool, annotations={'i': 1, 'j': 2})
        self.assert_rule_assume(seq, ({x@bool}, x@bool), {'i': 1, 'j': 2})

        t = Equal(f(x), g(y, k))
        seq = RuleAssume(t, annotations={'i': 1, 'j': 2})
        self.assert_rule_assume(seq, ({t}, t), {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertTrue(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_refl(self):
        self.assertRaises(TypeError, RuleRefl, 'abc')
        self.assertRaises(TypeError, RuleRefl, BaseType('x'))

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        l = Constant('l', a)
        f = Constant('f', a >> b)
        g = Constant('g', type=(a, b) >> a)

        seq = RuleRefl(x, annotations={'i': 1, 'j': 2})
        self.assert_rule_refl(seq, (set(), Equal(x, x)), {'i': 1, 'j': 2})

        seq = RuleRefl(x@bool, annotations={'i': 1, 'j': 2})
        self.assert_rule_refl(
            seq, (set(), Iff(x@bool, x@bool)), {'i': 1, 'j': 2})

        t = g(g(l, f(y)), f(x))
        seq = RuleRefl(t, annotations={'i': 1, 'j': 2})
        self.assert_rule_refl(seq, (set(), Equal(t, t)), {'i': 1, 'j': 2})

        self.assertFalse(seq.is_rule_assume())
        self.assertTrue(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertTrue(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_trans(self):
        x, y = Variables('x', 'y', bool)
        self.assertRaises(TypeError, RuleTrans, 0, 1)
        self.assertRaises(TypeError, RuleTrans, RuleRefl(x), x)
        self.assertRaises(TypeError, RuleTrans, x, RuleRefl(x))

        self.assertRaisesRegex(
            RuleError, 'not an equation',
            RuleTrans, RuleAssume(x@bool), RuleRefl(x))
        self.assertRaisesRegex(
            RuleError, 'not an equation',
            RuleTrans, RuleRefl(x), RuleAssume(x@bool))
        self.assertRaisesRegex(
            RuleError, r'not \(alpha\) equal',
            RuleTrans, RuleRefl(x), RuleRefl(y))

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        f = Constant('f', a >> b)
        g = Constant('g', type=(a, b) >> a)

        s1, s2 = RuleAssume(Equal(x, y)), RuleAssume(Equal(y, g(x, k)))
        seq = RuleTrans(s1, s2, annotations={'i': 1, 'j': 2})
        self.assert_rule_trans(
            seq, ({Equal(x, y), Equal(y, g(x, k))}, Equal(x, g(x, k))),
            {'i': 1, 'j': 2})

        s1, s2 = RuleRefl(x >> x), RuleRefl(y >> y)
        seq = RuleTrans(s1, s2, annotations={'i': 1, 'j': 2})
        self.assert_rule_trans(
            seq, (set(), Equal(x >> x, y >> y)), {'i': 1, 'j': 2})

        self.assertFalse(seq.is_rule_assume())
        self.assertTrue(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertFalse(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_mk_comb(self):
        x, y = Variables('x', 'y', bool)
        f, g = Variables('f', 'g', FunctionType(bool, bool))
        self.assertRaises(TypeError, RuleMkComb, 0, 1)
        self.assertRaises(TypeError, RuleMkComb, RuleRefl(f), x)
        self.assertRaises(TypeError, RuleMkComb, f, RuleRefl(x))

        self.assertRaisesRegex(
            RuleError, 'not an equation',
            RuleMkComb, RuleAssume(x@bool), RuleRefl(x))
        self.assertRaisesRegex(
            RuleError, 'not an equation',
            RuleMkComb, RuleRefl(x), RuleAssume(x@bool))
        self.assertRaisesRegex(
            RuleError, 'cannot apply',
            RuleMkComb, RuleRefl(x), RuleRefl(f))
        self.assertRaisesRegex(
            RuleError, 'cannot apply',
            RuleMkComb, RuleRefl(f), RuleRefl(x@BaseType('a')))

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        f = Constant('f', a >> b)
        g = Constant('g', type=(b, a) >> b)

        s1, s2 = RuleRefl(f), RuleRefl(x)
        seq = RuleMkComb(s1, s2, annotations={'i': 1, 'j': 2})
        self.assert_rule_mk_comb(
            seq, (set(), Equal(f(x), f(x))), {'i': 1, 'j': 2})

        s1, s2 = RuleAssume(Equal(f, g(k))), RuleAssume(Equal(x, y))
        seq = RuleMkComb(s1, s2, annotations={'i': 1, 'j': 2})
        self.assert_rule_mk_comb(
            seq, ({Equal(f, g(k)), Equal(x, y)}, Equal(f(x), g(k, y))),
            {'i': 1, 'j': 2})

        self.assertFalse(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertTrue(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_abs(self):
        x, y = Variables('x', 'y', bool)
        f, g = Variables('f', 'g', FunctionType(bool, bool))
        self.assertRaises(TypeError, RuleAbs, 0)
        self.assertRaises(TypeError, RuleAbs, x, x)
        self.assertRaises(TypeError, RuleAbs, f(x), RuleRefl(x))

        self.assertRaisesRegex(
            RuleError, 'not an equation',
            RuleAbs, x, RuleAssume(x@bool))
        self.assertRaisesRegex(
            RuleError, 'occurs free in hypothesis',
            RuleAbs, x, RuleAssume(Equal(x, y)))

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        f = Constant('f', a >> b)
        g = Constant('g', type=(b, a) >> b)

        seq = RuleAbs(
            y, RuleAssume(Equal(x, x)), annotations={'i': 1, 'j': 2})
        self.assert_rule_abs(
            seq, ({Equal(x, x)}, Equal(y >> x, y >> x)), {'i': 1, 'j': 2})

        t = Equal(x >> f(x), y >> k)
        seq = RuleAbs(x, RuleAssume(t), annotations={'i': 1, 'j': 2})
        self.assert_rule_abs(
            seq, ({t}, Equal(x >> t.left.right, x >> t.right)),
            {'i': 1, 'j': 2})

        self.assertFalse(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertFalse(seq.is_rule_mk_comb())
        self.assertTrue(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_beta(self):
        x, y = Variables('x', 'y', bool)
        f, g = Variables('f', 'g', FunctionType(bool, bool))
        self.assertRaises(TypeError, RuleBeta, 0)
        self.assertRaises(TypeError, RuleBeta, BoolType())
        self.assertRaises(TypeError, RuleBeta, x)
        self.assertRaises(TypeError, RuleBeta, (x >> x))
        self.assertRaises(TypeError, RuleBeta, f(x))

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', a)
        f = Constant('f', a >> b)
        g = Constant('g', type=(b, a) >> b)

        seq = RuleBeta(
            (x >> f(x))(x), annotations={'i': 1, 'j': 2})
        self.assert_rule_beta(
            seq, (set(), Equal((x >> f(x))(x), f(x)),), {'i': 1, 'j': 2})

        seq = RuleBeta(
            (x >> g(f(x), y))(k), annotations={'i': 1, 'j': 2})
        self.assert_rule_beta(
            seq, (set(), Equal((x >> g(f(x), y))(k), g(f(k), y))),
            {'i': 1, 'j': 2})

        self.assertFalse(RuleAssume(x@bool).is_rule_beta())
        self.assertFalse(RuleRefl(x).is_rule_beta())
        self.assertFalse(RuleRefl(f(x)).is_rule_beta())
        self.assertTrue(RuleBeta((y >> f(x))(k)).is_rule_beta())

        self.assertFalse(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertTrue(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertTrue(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_eq_mp(self):
        x, y = Variables('x', 'y', bool)
        self.assertRaises(TypeError, RuleEqMP, 0)
        self.assertRaises(TypeError, RuleEqMP, BoolType())
        self.assertRaises(TypeError, RuleEqMP, RuleRefl(x), x)

        x, y = Variables('x', 'y', bool)
        self.assertRaisesRegex(
            RuleError, 'not an equivalence',
            RuleEqMP, RuleAssume(x), RuleRefl(x))
        self.assertRaisesRegex(
            RuleError, r'not \(alpha\) equal',
            RuleEqMP, RuleRefl(x), RuleRefl(x))

        seq = RuleEqMP(
            RuleAssume(Equal(x, y)), RuleAssume(x),
            annotations={'i': 1, 'j': 2})
        self.assert_rule_eq_mp(
            seq, ({x, Equal(x, y)}, y), {'i': 1, 'j': 2})

        self.assertFalse(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertFalse(seq.is_rule_trans())
        self.assertFalse(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_deduct_antisym(self):
        x, y = Variables('x', 'y', bool)
        self.assertRaises(TypeError, RuleDeductAntisym, 0, 1)
        self.assertRaises(TypeError, RuleDeductAntisym, RuleRefl(x), x)

        x, y = Variables('x', 'y', bool)
        seq = RuleDeductAntisym(
            RuleAssume(x), RuleAssume(y),
            annotations={'i': 1, 'j': 2})
        self.assert_rule_deduct_antisym(
            seq, ({x, y}, Equal(x, y)), {'i': 1, 'j': 2})

        seq = RuleDeductAntisym(
            RuleRefl(x), RuleAssume(Equal(y, y)), annotations={'i': 1})
        self.assert_rule_deduct_antisym(
            seq, ({Equal(y, y)}, Equal(Equal(x, x), Equal(y, y))), {'i': 1})

        self.assertFalse(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertTrue(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertTrue(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_inst_type(self):
        x, y = Variables('x', 'y', bool)
        self.assertRaises(TypeError, RuleInstType, 0, 1)
        self.assertRaises(TypeError, RuleInstType, {}, x)

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        f = Constant('f', a >> a)
        g = Constant('g', type=(b, a) >> b)

        seq = RuleInstType(
            {a: BoolType()}, RuleAssume(Equal(x, f(x))),
            annotations={'i': 1, 'j': 2})

        self.assert_rule_inst_type(
            seq, ({Equal(x@bool, (f@FunctionType(bool, bool))(x@bool))},
                  Equal(x@bool, (f@FunctionType(bool, bool))(x@bool))),
            {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertTrue(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertTrue(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())

    def test_rule_subst(self):
        x, y = Variables('x', 'y', bool)
        self.assertRaises(TypeError, RuleSubst, 0, 1)
        self.assertRaises(TypeError, RuleSubst, {}, x)

        a, b = TypeVariables('a', 'b')
        x, y = Variables('x', 'y', a)
        k = Constant('k', b)
        f = Constant('f', a >> a)
        g = Constant('g', type=(b, a) >> a)

        seq = RuleSubst(
            {x: g(k, f(x))}, RuleAssume(Equal(x, f(x))),
            annotations={'i': 1, 'j': 2})
        self.assert_rule_subst(
            seq, ({Equal(g(k, f(x)), f(g(k, f(x))))},
                  Equal(g(k, f(x)), f(g(k, f(x))))),
            {'i': 1, 'j': 2})

        self.assertTrue(seq.is_rule_assume())
        self.assertFalse(seq.is_rule_refl())
        self.assertTrue(seq.is_rule_trans())
        self.assertTrue(seq.is_rule_mk_comb())
        self.assertFalse(seq.is_rule_abs())
        self.assertFalse(seq.is_rule_beta())
        self.assertTrue(seq.is_rule_eq_mp())
        self.assertFalse(seq.is_rule_deduct_antisym())
        self.assertTrue(seq.is_rule_inst_type())
        self.assertTrue(seq.is_rule_subst())


if __name__ == '__main__':
    main()
