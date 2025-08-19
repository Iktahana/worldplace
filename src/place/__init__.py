"""

"""

__STEP__ = 0.0001
__SCALE__ = int(1 / __STEP__)


def coord_to_index(value: float) -> int:
    """
    Convert latitude and longitude floating point numbers >> block index
    For example, 0.0001 -> 1, 1.0 -> 10000
    """
    return int(value * __SCALE__)


def index_to_coord(index: int) -> float:
    """
    Convert block index back >> latitude and longitude
    For example, 1 -> 0.0001, 10000 -> 1.0
    """
    return float(index) * __STEP__
