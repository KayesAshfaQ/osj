"""Release checks must reject unsafe origins and incomplete app deployments."""

import unittest
from unittest.mock import patch

from web_deployment import clean_https_origin, verify_app


class WebDeploymentTests(unittest.TestCase):
    def test_release_origin_must_be_clean_https(self):
        self.assertEqual(clean_https_origin("https://api.example.com/"), "https://api.example.com")
        for value in [
            "",
            "http://localhost:8000",
            "https://user:pass@example.com",
            "https://example.com/api",
            "https://example.com?q=1",
            "https://example.com#x",
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                clean_https_origin(value)

    def test_landing_page_cannot_pass_as_flutter_app(self):
        with patch("web_deployment.fetch", return_value=b"<html>Landing page</html>"):
            with self.assertRaisesRegex(ValueError, "Flutter"):
                verify_app("https://app.example.com")

    def test_spa_fallback_cannot_pass_as_bootstrap_javascript(self):
        with patch(
            "web_deployment.fetch",
            side_effect=[b'<script src="flutter_bootstrap.js"></script>', b"<!DOCTYPE html><html>fallback</html>"],
        ):
            with self.assertRaisesRegex(ValueError, "bootstrap"):
                verify_app("https://app.example.com")

    def test_app_requires_html_and_real_bootstrap(self):
        with patch(
            "web_deployment.fetch",
            side_effect=[b'<script src="flutter_bootstrap.js"></script>', b"_flutter.loader.load();"],
        ):
            verify_app("https://app.example.com")


if __name__ == "__main__":
    unittest.main()
