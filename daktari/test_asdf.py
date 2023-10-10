import unittest
from daktari.asdf import get_tool_version_from_string


class TestGetToolVersionFromString(unittest.TestCase):
    def test_valid_tool(self):
        content = """1password-cli 2.19.0
cloud-sql-proxy 2.6.1
# Comment line
daktari 0.0.140"""
        self.assertEqual(get_tool_version_from_string("1password-cli", content), "2.19.0")

    def test_tool_with_comment(self):
        content = """1password-cli 2.19.0 # also update in .daktari.py
cloud-sql-proxy 2.6.1"""
        self.assertEqual(get_tool_version_from_string("1password-cli", content), "2.19.0")

    def test_tool_not_present(self):
        content = """1password-cli 2.19.0
cloud-sql-proxy 2.6.1"""
        self.assertIsNone(get_tool_version_from_string("invalid-tool", content))

    def test_empty_content(self):
        content = ""
        self.assertIsNone(get_tool_version_from_string("1password-cli", content))


if __name__ == "__main__":
    unittest.main()
