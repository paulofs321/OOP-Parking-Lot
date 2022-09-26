from enum import Enum


class Size(Enum):
    """
    Enum class for sizes
    """
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


class EntryPoint(Enum):
    """
    Enum class for the entrypoints
    """
    A = 0
    B = 1
    C = 2
    D = 4
    E = 5


class Rates(Enum):
    """
    Enum class for the rates
    """
    SMALL = 20
    MEDIUM = 60
    LARGE = 100
    DAY_OVER = 5000


class Hours(Enum):
    """
    Enum class for the number of hours within flat rate and continuous
    """
    WITHIN_FLAT_RATE = 3
    WITHIN_CONTINUOUS = 1
    IN_A_DAY = 24
