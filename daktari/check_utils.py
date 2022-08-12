from typing import Union, Type, Set

from daktari.check import Check


def get_all_dependent_check_names(check: Union[Check, Type[Check]]) -> Set[str]:
    dependents = {dep.name for dep in check.depends_on}
    sub_dependents = [get_all_dependent_check_names(dep) for dep in check.depends_on]
    flat_sub_dependents = {item for subset in sub_dependents for item in subset}
    result = flat_sub_dependents.union(dependents)
    if result.__contains__(check.name):
        raise RecursionError(f"Check {check.name} has cyclic dependencies")

    return result
