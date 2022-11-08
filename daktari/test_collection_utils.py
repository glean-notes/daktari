import unittest

from daktari.collection_utils import flatten


class TestCollectionUtils(unittest.TestCase):
    def test_flatten(self):
        original = [{"A", "B", "C"}, {"B", "D"}, {"A", "Z"}, {}]
        result = flatten(original)
        self.assertEqual({"A", "B", "C", "D", "Z"}, result)


if __name__ == "__main__":
    unittest.main()
