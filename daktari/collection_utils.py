from typing import TypeVar, List, Set

T = TypeVar("T")


def flatten(original: List[Set[T]]) -> Set[T]:
    return {item for subset in original for item in subset}
