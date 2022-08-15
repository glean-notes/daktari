from typing import Union, Type, Set

from daktari.check import Check
from daktari.collection_utils import flatten


class CyclicCheckException(Exception):
    def __init__(self, message):
        super().__init__(message)


def check_for_cycles(check: Union[Check, Type[Check]], prev_parents: Set[str]):
    if check.name in prev_parents:
        raise CyclicCheckException(f"Check [{check.name}] has cyclic dependencies")
    for sub_check in check.depends_on:
        check_for_cycles(sub_check, prev_parents.union({check.name}))


def get_all_dependent_check_names(check: Union[Check, Type[Check]]) -> Set[str]:
    check_for_cycles(check, set())
    return _get_all_dependent_check_names_recursive(check)


def _get_all_dependent_check_names_recursive(check: Union[Check, Type[Check]]) -> Set[str]:
    sub_dependents = [_get_all_dependent_check_names_recursive(dep) for dep in check.depends_on]
    flat_sub_dependents = flatten(sub_dependents)
    return flat_sub_dependents.union({dep.name for dep in check.depends_on})
