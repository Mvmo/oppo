from dataclasses import dataclass
from enum import Enum, auto
from typing import *

type_name_dict = {
    "int": "sick::int",
    "string": "sick::string",
    "bool": "sick::bool"
}

keywords = [
    "proc",
    "if",
    "else",
    "while",
    "do",
    "end",
    "as",
    "include"
]

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
    "sizeof",
    "swap",
    "dup", 
    "println",
    "print"
]

@dataclass
class TokenLocation:
    line_content: str
    row: int
    column_start: int
    column_end: int

class TokenType(Enum):
    INTRINSIC = auto()
    KEYWORD = auto()
    IDENTIFIER = auto()
    INT = auto()
    STRING = auto()
    BOOLEAN = auto()
    TYPE = auto()
    INCLUDE = auto()

@dataclass
class Token:
    literal: str
    location: TokenLocation
    typ: TokenType

def tokenize(input: str, debug = True) -> "list[Token]":
    lines = input.splitlines(keepends=False)
    position: Tuple[int, int] = (0, 0)

    current_token: Token = Token(literal="",location=TokenLocation("", position[0], position[1], 0), typ=None)
    tokens: list[Token] = []

    def inc_column():
        nonlocal position
        
        row, column = position
        position = (row, column + 1)

    def inc_row():
        nonlocal position
        
        row, column = position
        position = (row + 1, column)

    def flush_token():
        nonlocal current_token
        nonlocal tokens
        nonlocal lines

        if current_token == None or len(current_token.literal) == 0:
            return
        elif current_token.literal == "include":
            current_token.typ = TokenType.INCLUDE
        elif current_token.literal in type_name_dict.keys():
            current_token.literal = type_name_dict[current_token.literal]
            current_token.typ = TokenType.TYPE
        elif current_token.literal in intrinsics:
            current_token.typ = TokenType.INTRINSIC
        elif current_token.literal in keywords:
            current_token.typ = TokenType.KEYWORD
        elif current_token.literal.startswith("\"") and current_token.literal.endswith("\""):
            token_before = tokens[len(tokens) - 1]
            if token_before.typ == TokenType.INCLUDE:
                tokens[len(tokens) - 1] = Token(current_token.literal.replace("\"", ""), token_before.location, token_before.typ)
                current_token = Token(literal="",location=TokenLocation("", position[0], position[1], 0), typ=None)
                return
            current_token.typ = TokenType.STRING
        elif current_token.literal.isnumeric():
            current_token.typ = TokenType.INT
        elif current_token.literal == "true" or current_token.literal == "false":
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
        if len(line) == 0:
            inc_row()
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
                inc_column()
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
    return tokens
