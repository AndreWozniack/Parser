from dataclasses import dataclass
from TokenType import TokenType

@dataclass
class Token:
    value: str
    token_class: TokenType
    row: int
    column: int

    def __str__(self):
        return f"<{self.token_class.name}('{self.value}') @ {self.row}:{self.column}>"

    def __repr__(self):
        return self.__str__()

    def tokenToDict(self):
        return {
            "value": self.value,
            "token_class": self.token_class.name,
            "row": self.row,
            "column": self.column
        }