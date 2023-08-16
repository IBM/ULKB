# Copyright (C) 2023 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from ulkb import *

from .tests import ULKB_TestCase, main


class TestRuleZ3(ULKB_TestCase):

    def test_rule_z3(self):
        # ⊬ ⊥
        self.assertRaisesRegex(
            RuleError, 'failed to prove', RuleZ3, Falsity())

        # ⊢ ⊤
        self.assert_sequent(RuleZ3(Truth()), (frozenset(), Truth()))

        # ∀ x, P x ⊢ P c
        a = TypeVariable('a')
        x = Variable('x', a)
        c = Constant('c', a)
        P = Constant('P', FunctionType(a, bool))
        new_axiom(Forall(x, P(x)))
        self.assert_sequent(RuleZ3(P(c)), (frozenset(), P(c)))

        # ∀ x, P x ⊬ ¬P c
        self.assertRaisesRegex(
            RuleError, 'failed to prove', RuleZ3, ~P(c))

        # ⊢ 3 < 4
        self.assert_sequent(
            RuleZ3(lt_z(3, 4)), (frozenset(), lt_z(3, 4)))

        # ⊬ 4 < 3
        self.assertRaisesRegex(
            RuleError, 'failed to prove', RuleZ3, lt_z(4, 3))


if __name__ == '__main__':
    main()
