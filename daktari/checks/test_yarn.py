import unittest

from daktari.checks.yarn import YarnNpmScope, match_scope, yarnrc_contains_scope

TEST_SCOPE_NAME = "scope"
TEST_REGISTRY_SERVER = "https://registry-server.glean.co"
TEST_REGISTRY_SERVER_2 = "https://registry-server.sonocent.com"
TEST_PUBLISH_REGISTRY = "https://publish-registry.glean.co"
TEST_PUBLISH_REGISTRY_2 = "https://publish-registry.sonocent.com"
TEST_AUTH_TOKEN = "ABCD1234"


class TestYarn(unittest.TestCase):
    def test_matches_scope_publish_registry(self):
        template_scope = YarnNpmScope(TEST_SCOPE_NAME, TEST_PUBLISH_REGISTRY)
        matching_yaml = {"npmPublishRegistry": TEST_PUBLISH_REGISTRY}
        non_matching_yaml_1 = {"npmPublishRegistry": TEST_PUBLISH_REGISTRY_2}
        non_matching_yaml_2 = {}

        self.assertTrue(match_scope(template_scope, matching_yaml))
        self.assertFalse(match_scope(template_scope, non_matching_yaml_1))
        self.assertFalse(match_scope(template_scope, non_matching_yaml_2))

    def test_matches_scope_registry_server(self):
        template_scope = YarnNpmScope("scope", npmRegistryServer=TEST_REGISTRY_SERVER)
        matching_yaml = {"npmRegistryServer": TEST_REGISTRY_SERVER}
        non_matching_yaml_1 = {"npmRegistryServer": TEST_REGISTRY_SERVER_2}
        non_matching_yaml_2 = {}

        self.assertTrue(match_scope(template_scope, matching_yaml))
        self.assertFalse(match_scope(template_scope, non_matching_yaml_1))
        self.assertFalse(match_scope(template_scope, non_matching_yaml_2))

    def test_matches_scope_with_auth_token_required(self):
        template_scope = YarnNpmScope("scope", requireNpmAuthToken=True)
        matching_yaml = {"npmAuthToken": "ABCD1234"}
        non_matching_yaml = {}

        self.assertTrue(match_scope(template_scope, matching_yaml))
        self.assertFalse(match_scope(template_scope, non_matching_yaml))

    def test_finds_scope_in_yarnrc(self):
        yarnrc = {
            "npmScopes": {
                "glean": {"npmRegistryServer": TEST_REGISTRY_SERVER, "npmPublishRegistry": TEST_PUBLISH_REGISTRY},
                "sonocent": {"npmRegistryServer": TEST_REGISTRY_SERVER_2, "npmAuth": "TOKEN"},
            }
        }
        existing_scope_1 = YarnNpmScope("glean", npmPublishRegistry=TEST_PUBLISH_REGISTRY)
        existing_scope_2 = YarnNpmScope("sonocent", npmRegistryServer=TEST_REGISTRY_SERVER_2)
        # Incorrect scope configuration:
        nonexistent_scope_1 = YarnNpmScope("glean", npmRegistryServer="http://localhost")
        # Auth token required, none supplied:
        nonexistent_scope_2 = YarnNpmScope("glean", npmRegistryServer=TEST_REGISTRY_SERVER, requireNpmAuthToken=True)
        # Wrong name
        nonexistent_scope_3 = YarnNpmScope("walter")

        self.assertTrue(yarnrc_contains_scope(yarnrc, existing_scope_1))
        self.assertTrue(yarnrc_contains_scope(yarnrc, existing_scope_2))
        self.assertFalse(yarnrc_contains_scope(yarnrc, nonexistent_scope_1))
        self.assertFalse(yarnrc_contains_scope(yarnrc, nonexistent_scope_2))
        self.assertFalse(yarnrc_contains_scope(yarnrc, nonexistent_scope_3))


if __name__ == "__main__":
    unittest.main()
