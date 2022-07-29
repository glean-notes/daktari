import unittest
from daktari.check import Check, CheckResult
from daktari.check_utils import get_all_dependent_check_names


###
# Dummy checks set up with dependencies as follows (A <- B means "B depends on A")
#
#
#   A <- B <- C <- E
#             D <- E
#
class DummyCheck(Check):
    def check(self) -> CheckResult:
        return self.passed("no check")


class CheckA(DummyCheck):
    name = "A"


class CheckB(DummyCheck):
    name = "B"
    depends_on = [CheckA]


class CheckC(DummyCheck):
    name = "C"
    depends_on = [CheckB]


class CheckD(DummyCheck):
    name = "D"


class CheckE(DummyCheck):
    name = "E"
    depends_on = [CheckC, CheckD]


class TestCheckUtils(unittest.TestCase):
    def test_get_all_dependent_check_names(self):
        self.assertEqual(["A"], get_all_dependent_check_names(CheckA))
        self.assertEqual(["A", "B"], get_all_dependent_check_names(CheckB))
        self.assertEqual(["A", "B", "C"], get_all_dependent_check_names(CheckC))
        self.assertEqual(["A", "B", "C", "D", "E"], get_all_dependent_check_names(CheckE))


if __name__ == "__main__":
    unittest.main()
