from dataclasses import dataclass
from distutils.errors import LibError
from enum import Enum, auto
from turtle import pos, position
from typing import *

intrinsics = [
    "+",
    "-",
    "*",
    "/",
    "~",
    "=",
    "<",
    ">",
    "<=", 
    ">=", 
    "dup", 
    "if", 
    "else", 
    "while", 
    "do", 
    "end", 
    "as"
]

@dataclass
class TokenLocation:
    line_content: str
    row: int
    column_start: int
    column_end: int

class TokenType(Enum):
    INTRINSIC = auto()
    IDENTIFIER = auto()
    INT = auto()
    STRING = auto()
    BOOLEAN = auto()


@dataclass
class Token:
    literal: str
    location: TokenLocation
    typ: TokenType

def tokenize(input: str, debug = True):
    lines = input.splitlines(keepends=False)
    position: Tuple[int, int] = (0, 0)

    current_token: Token = Token(literal="",location=TokenLocation("", position[0], position[1], 0), typ=None)
    tokens: list[Token] = []

    def inc_column():
        nonlocal position
        
        row, column = position
        position = (row, column + 1)

        return position

    def inc_row():
        nonlocal position
        
        row, column = position
        position = (row + 1, column)

        return position

    def flush_token():
        nonlocal current_token
        nonlocal tokens
        nonlocal lines

        if current_token == None or len(current_token.literal) == 0:
            return
        elif current_token.literal in intrinsics:
            current_token.typ = TokenType.INTRINSIC
        elif current_token.literal.startswith("\"") and current_token.literal.endswith("\""):
            current_token.typ = TokenType.STRING
        elif current_token.literal.isnumeric():
            current_token.typ = TokenType.INT
        elif current_token.literal == "true":
            current_token.typ = TokenType.BOOLEAN
        else:
            current_token.typ = TokenType.IDENTIFIER
        
        current_token.location = TokenLocation(lines[position[0]][position[1]], position[0], position[1], position[1] + len(current_token.literal))
        tokens.append(current_token)
        
        if debug: print(f"[Tokenizer] + {current_token.typ}-Token ('{current_token.literal}')")

        current_token = Token(literal="",location=TokenLocation("", position[0], position[1], 0), typ=None)
        
    def line_start(line: str) -> int:
        start = 0
        char = line[start]
        while start < len(line) and (char == " " or char == "\t"):
            start += 1
            char = line[start]
            continue
        return start

    while position[0] < len(lines):
        line = lines[position[0]]
        if len(line) == 0 or (len(line) == 1 and (line[0] == " " or line[0] == "\t")):
            position = inc_row()
            continue
        row, _ = position
        position = (row, line_start(line))
        while position[1] < len(line):
            char = line[position[1]]
            if (char == " " or char == "\t" or char == "\n") and position[1] < len(line):
                flush_token()
                char = line[position[1]]
                inc_column()
                current_token.location = TokenLocation("", position[0], position[1], 0)
                continue
            if char == "\"":
                flush_token()
                current_token.literal = char
                while position[1] < len(line):
                    char = line[position[1]]
                    current_token.literal += char
                    if char == "\"":
                        flush_token()
                        inc_column()
                        break
                    inc_column()
                    continue
                continue
            current_token.literal += char
            if position[1] + 1 == len(line):
                flush_token()
            inc_column()
        inc_row()
