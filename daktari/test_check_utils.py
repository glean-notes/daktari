import unittest

from daktari.check_utils import get_all_dependent_check_names, CyclicCheckException
from daktari.test_check_factory import DummyCheck


class TestCheckUtils(unittest.TestCase):
    def test_get_all_dependent_check_names(self):
        # Dummy checks set up with dependencies as follows (A <- B means "B depends on A")
        #
        #   A <- B <- C <- E
        #             D <- E
        #
        check_a = DummyCheck("A")
        check_b = DummyCheck("B", [check_a])
        check_c = DummyCheck("C", [check_b])
        check_d = DummyCheck("D")
        check_e = DummyCheck("E", [check_c, check_d])

        self.assertEqual(set(), get_all_dependent_check_names(check_a))
        self.assertEqual({"A"}, get_all_dependent_check_names(check_b))
        self.assertEqual({"A", "B"}, get_all_dependent_check_names(check_c))
        self.assertEqual({"A", "B", "C", "D"}, get_all_dependent_check_names(check_e))

    def test_self_cycle(self):
        check = DummyCheck("A")
        check.depends_on = [check]
        with self.assertRaises(CyclicCheckException):
            get_all_dependent_check_names(check)

    def test_simple_cycle(self):
        check_a = DummyCheck("A")
        check_b = DummyCheck("B")

        check_a.depends_on = [check_b]
        check_b.depends_on = [check_a]
        with self.assertRaises(CyclicCheckException):
            get_all_dependent_check_names(check_a)

    def test_larger_cycle(self):
        check_a = DummyCheck("A")
        check_b = DummyCheck("B")
        check_c = DummyCheck("C")

        check_a.depends_on = [check_b]
        check_b.depends_on = [check_c]
        check_c.depends_on = [check_a]

        with self.assertRaises(CyclicCheckException):
            get_all_dependent_check_names(check_a)

    def test_depends_on_cycle(self):
        check_a = DummyCheck("A")
        check_b = DummyCheck("B")
        check_c = DummyCheck("C")
        check_d = DummyCheck("D")

        check_a.depends_on = [check_b]
        check_b.depends_on = [check_c]
        check_c.depends_on = [check_d]
        check_d.depends_on = [check_b]

        with self.assertRaises(CyclicCheckException):
            get_all_dependent_check_names(check_a)


if __name__ == "__main__":
    unittest.main()
