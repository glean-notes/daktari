import unittest

from .java import parse_java_version_output
from semver import VersionInfo


class TestJava(unittest.TestCase):
    def test_parse_non_semver_format_version(self):
        # JRE versions prior to 9 do not use semver format
        version_output = """openjdk version "1.8.0_292"
OpenJDK Runtime Environment (build 1.8.0_292-8u292-b10-0ubuntu1~20.04-b10)
OpenJDK 64-Bit Server VM (build 25.292-b10, mixed mode)
"""
        version = parse_java_version_output(version_output)
        self.assertEqual(version, VersionInfo(8))

    def test_parse_semver_format_version(self):
        version_output = """openjdk version "11.0.9" 2020-10-20
OpenJDK Runtime Environment AdoptOpenJDK (build 11.0.9+11)
OpenJDK 64-Bit Server VM AdoptOpenJDK (build 11.0.9+11, mixed mode)
"""
        version = parse_java_version_output(version_output)
        self.assertEqual(version, VersionInfo(11, 0, 9))

    def test_parse_unknown_format_version(self):
        version_output = 'openjdk version "a.b.c"'
        version = parse_java_version_output(version_output)
        self.assertEqual(version, None)

    def test_parse_unknown_format_output(self):
        version_output = """

Command 'java' not found, but can be installed with:

sudo apt install openjdk-11-jre-headless  # version 11.0.11+9-0ubuntu2~20.04, or
sudo apt install default-jre              # version 2:1.11-72
sudo apt install openjdk-13-jre-headless  # version 13.0.7+5-0ubuntu1~20.04
sudo apt install openjdk-16-jre-headless  # version 16.0.1+9-1~20.04
sudo apt install openjdk-8-jre-headless   # version 8u292-b10-0ubuntu1~20.04
sudo apt install openjdk-14-jre-headless  # version 14.0.2+12-1~20.04

"""
        version = parse_java_version_output(version_output)
        self.assertEqual(version, None)


if __name__ == "__main__":
    unittest.main()