from enum import Enum, auto

class TokenType(Enum):
    INTEGER_NUMBER = auto()
    REAL_NUMBER = auto()
    LEFT_PARENTHESIS = auto()
    RIGHT_PARENTHESIS = auto()
    OPERATOR = auto()
    KEYWORD = auto()
    ERROR = auto()