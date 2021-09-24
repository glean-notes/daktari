import logging
from typing import Optional
from xml.etree.ElementTree import Element, ElementTree, ParseError

from daktari.check import Check, CheckResult
from daktari.file_utils import file_exists


class XmlFileXPathCheck(Check):
    file_path = ""
    xpath_query = "./"
    pass_fail_message = ""

    def validate_query_result(self, result: Optional[Element]) -> bool:
        return result is not None

    def perform_query(self) -> bool:
        if not file_exists(self.file_path):
            logging.debug(f"File {self.file_path} does not exist")
            return False

        try:
            doc = ElementTree(file=self.file_path)
        except ParseError:
            logging.debug(f"Error parsing {self.file_path}", exc_info=True)
            return False

        query_result = doc.find(self.xpath_query)
        return self.validate_query_result(query_result)

    def check(self) -> CheckResult:
        success = self.perform_query()
        return self.verify(success, self.pass_fail_message)
