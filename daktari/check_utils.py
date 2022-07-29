from typing import Union, Type, List

from daktari.check import Check


def get_all_dependent_check_names(check: Union[Check, Type[Check]]) -> List[str]:
    dependents = [get_all_dependent_check_names(dep) for dep in check.depends_on]
    flat_dependents = [item for sublist in dependents for item in sublist]
    return flat_dependents + [check.name]
