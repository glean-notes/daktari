from typing import Union, Type, Set

from daktari.check import Check


class CyclicCheckException(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_all_dependent_check_names(check: Union[Check, Type[Check]]) -> Set[str]:
    return _get_all_dependent_check_names_recursive(check, set())


def _get_all_dependent_check_names_recursive(check: Union[Check, Type[Check]], prev_parents: Set[str]) -> Set[str]:
    prev_parents = prev_parents.union({check.name})
    dependents = {dep.name for dep in check.depends_on}
    intersection = dependents.intersection(prev_parents)
    if len(intersection) > 0:
        raise CyclicCheckException(f"Check [{intersection.pop()}] has cyclic dependencies")

    sub_dependents = [_get_all_dependent_check_names_recursive(dep, prev_parents) for dep in check.depends_on]
    flat_sub_dependents = {item for subset in sub_dependents for item in subset}
    return flat_sub_dependents.union(dependents)
