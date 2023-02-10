import logging
import os
from datetime import datetime
from OpenSSL import crypto

from daktari.check import Check, CheckResult
from daktari.os import OS


class CertificateIsNotExpired(Check):
    name = "certificate.isNotExpired"

    def __init__(self, certificate_path: str):
        self.certificate_path = certificate_path
        self.suggestions = {
            OS.GENERIC: f"Regenerate the certificate at {certificate_path}",
        }

    def check(self) -> CheckResult:
        with open(self.certificate_path, "rb") as f:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
            logging.debug(f"Raw expiry: f{cert.get_notAfter()}")

            expiry = datetime.strptime(cert.get_notAfter().decode(), "%Y%m%d%H%M%SZ")
            if expiry > datetime.now():
                return self.passed(f"{os.path.basename(self.certificate_path)} is not expired")
            else:
                return self.failed(f"{os.path.basename(self.certificate_path)} expired on {expiry}")
