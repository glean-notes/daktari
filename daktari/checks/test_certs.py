import unittest
from unittest import mock

from daktari.check import CheckStatus
from daktari.checks.certs import CertificateIsNotExpired
from daktari.resource_utils import get_resource_path


class TestCertificateIsNotExpired(unittest.TestCase):
    @mock.patch("daktari.checks.certs.crypto.load_certificate")
    def test_passes_with_warning_if_cannot_determine_expiry(self, mock_get_not_after):
        mock_get_not_after.return_value.get_notAfter.return_value = None
        check = CertificateIsNotExpired(get_resource_path("mock_cert.pem").__str__())
        result = check.check()
        self.assertEqual(result.status, CheckStatus.PASS_WITH_WARNING)
        self.assertEqual(result.summary, "Unable to determine expiry date of mock_cert.pem")

    @mock.patch("daktari.checks.certs.crypto.load_certificate")
    def test_passes_for_valid_cert(self, mock_get_not_after):
        mock_get_not_after.return_value.get_notAfter.return_value = b"20501231235959Z"
        check = CertificateIsNotExpired(get_resource_path("mock_cert.pem").__str__())
        result = check.check()
        self.assertEqual(result.status, CheckStatus.PASS)
        self.assertEqual(result.summary, "mock_cert.pem is not expired")

    @mock.patch("daktari.checks.certs.crypto.load_certificate")
    def test_fails_for_expired_cert(self, mock_get_not_after):
        mock_get_not_after.return_value.get_notAfter.return_value = b"20201231235959Z"
        check = CertificateIsNotExpired(get_resource_path("mock_cert.pem").__str__())
        result = check.check()
        self.assertEqual(result.status, CheckStatus.FAIL)
        self.assertEqual(result.summary, "mock_cert.pem expired on 2020-12-31 23:59:59")
