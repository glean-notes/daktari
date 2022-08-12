import unittest

from daktari.check_sorter import sort_checks
from daktari.check_utils import CyclicCheckException
from daktari.test_check_factory import DummyCheck


class TestCheckSorter(unittest.TestCase):
    def test_raises_error_if_cycle_found(self):
        check_a = DummyCheck("a")
        check_b = DummyCheck("b")

        check_a.depends_on = [check_b]
        check_b.depends_on = [check_a]

        with self.assertRaises(CyclicCheckException):
            sort_checks([check_a, check_b])

    def test_sorts_into_right_order(self):
        parent_check_a = DummyCheck("parent.a")
        sub_check_a_1 = DummyCheck("sub.check.a.1", [parent_check_a])
        sub_check_a_2 = DummyCheck("sub.check.a.2", [parent_check_a])
        sub_sub_check_a = DummyCheck("sub.sub.check.a", [sub_check_a_1, sub_check_a_2])

        parent_check_b = DummyCheck("parent.b")
        sub_check_b_1 = DummyCheck("sub.check.b.1", [parent_check_b])
        sub_check_b_2 = DummyCheck("sub.check.b.2", [parent_check_b])
        sub_check_b_3 = DummyCheck("sub.check.b.3", [parent_check_b])

        sub_check_a_b = DummyCheck("sub.check.a.b", [parent_check_b, parent_check_a])

        free_check_1 = DummyCheck("free.check.1")
        free_check_2 = DummyCheck("free.check.2")

        unsorted_list = [
            sub_check_b_1,
            sub_sub_check_a,
            parent_check_b,
            sub_check_b_3,
            sub_check_a_b,
            free_check_1,
            sub_check_b_2,
            sub_check_a_2,
            parent_check_a,
            free_check_2,
            sub_check_a_1,
        ]

        sorted_checks = [check.name for check in sort_checks(unsorted_list)]
        self.assertGreater(sorted_checks.index("sub.check.a.1"), sorted_checks.index("parent.a"))
        self.assertGreater(sorted_checks.index("sub.check.a.2"), sorted_checks.index("parent.a"))
        self.assertGreater(sorted_checks.index("sub.sub.check.a"), sorted_checks.index("sub.check.a.1"))
        self.assertGreater(sorted_checks.index("sub.sub.check.a"), sorted_checks.index("sub.check.a.2"))

        self.assertGreater(sorted_checks.index("sub.check.b.1"), sorted_checks.index("parent.b"))
        self.assertGreater(sorted_checks.index("sub.check.b.2"), sorted_checks.index("parent.b"))
        self.assertGreater(sorted_checks.index("sub.check.b.3"), sorted_checks.index("parent.b"))

        self.assertGreater(sorted_checks.index("sub.check.a.b"), sorted_checks.index("parent.a"))
        self.assertGreater(sorted_checks.index("sub.check.a.b"), sorted_checks.index("parent.b"))


if __name__ == "__main__":
    unittest.main()
