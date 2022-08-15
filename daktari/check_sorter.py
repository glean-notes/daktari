from typing import Dict, List, Set, TypeVar

from daktari.check import Check
from daktari.check_utils import get_all_dependent_check_names


def dependency_graph(checks: List[Check]) -> Dict[str, Set[str]]:
    return {check.name: get_all_dependent_check_names(check) for check in checks}


T = TypeVar("T")


def stable_topological_sort(items: List[T], dependencies: Dict[T, Set[T]]) -> List[T]:
    result = items.copy()
    for i in range(len(items)):
        for j in range(i):
            if result[i] in dependencies[result[j]]:
                item = result[i]
                del result[i]
                result.insert(j, item)
    return result


def sort_checks(checks: List[Check]) -> List[Check]:
    graph = dependency_graph(checks)
    check_names = [check.name for check in checks]
    sorted_check_names = stable_topological_sort(check_names, graph)

    def get_topo_order(check: Check):
        return sorted_check_names.index(check.name)

    return sorted(checks, key=get_topo_order)
