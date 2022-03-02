import argparse
from dataclasses import dataclass
from enum import Enum, auto
from typing import *
import sys

oppo_version = "0.0.1"
stack = []


def lex_file(file_path: str):
    with open(file_path, "r") as file:
        return lex_lines(file.readlines())


Location = Tuple[str, int, int]


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INT = auto()
    STRING = auto()
    BOOLEAN = auto()


@dataclass
class Token:
    literal: str


def tokenize(lines: str):

    pass


def lex_lines(lines: str):
    tokens = []

    for line in lines:
        splitted = line.strip().split(" ")
        if len(splitted) == 1 and splitted[0] == "":
            continue

        stack = []

        for token in splitted:
            if token == "#":
                break

            tokens.append(token)
    return tokens


reserverd_tokens = ["+", "-", "*", "/", "~", "=", "<", ">",
                    "<=", ">=", "dup", "if", "else", "while", "do", "end", "as"]


def tokens_to_instructions(tokens):
    instructions = []
    stack = []

    def append_instruction(x: tuple, array=instructions):
        instructions.append(
            (x[0], x[1] if len(x) == 2 else None, len(instructions)))
        return x

    index = 0
    while index < len(tokens):
        token = tokens[index]
        ri = len(instructions)
        index += 1
        if token.isnumeric():
            append_instruction(("push", int(token)))
        elif token == "+":
            append_instruction(("add", ))
        elif token == "-":
            append_instruction(("sub", ))
        elif token == "*":
            append_instruction(("mul", ))
        elif token == "/":
            append_instruction(("div", ))
        elif token == "~":
            append_instruction(("dump", ))
        elif token == "=":
            append_instruction(("cmp", ))
        elif token == "<":
            append_instruction(("lt", ))
        elif token == "<=":
            append_instruction(("lte", ))
        elif token == ">":
            append_instruction(("gt", ))
        elif token == ">=":
            append_instruction(("gte", ))
        elif token == "dup":
            append_instruction(("dup", ))
        elif token == "if":
            instruction = ("cjmp", ("if", ri))
            stack.append(instruction)
            # first param is where to jump if true and end param is where to jmp if false
            append_instruction(instruction)
        elif token == "else":
            enclosing = stack.pop()
            if_index = enclosing[1][1]

            instructions[if_index] = ("cjmp", (if_index + 1, ri + 1))
            instruction = ("jmp", ("else", ri))

            stack.append(instruction)
            append_instruction(instruction)
        elif token == "while":
            instruction = (f"$~while{len(instructions)}:", )
            stack.append(instruction)
            append_instruction(instruction)
        elif token == "do":
            enclosing = stack.pop()
            instruction = ("cjmp", ("do", enclosing[0], ri))
            stack.append(instruction)
            append_instruction(instruction)
        elif token == "end":
            enclosing = stack.pop()
            typ = enclosing[1][0]
            if typ == "if":
                if_index = enclosing[1][1]
                instructions[if_index] = (
                    "cjmp", (if_index + 1, ri))
            if typ == "else":
                else_index = enclosing[1][1]
                instructions[else_index] = ("jmp", (ri))
            if typ == "do":
                while_label = enclosing[1][1]
                do_index = enclosing[1][2]
                instructions[do_index] = ("cjmp", (do_index + 1, ri + 1))
                append_instruction((f"goto {while_label}".removesuffix(":"), ))
        elif token == "as":
            if len(tokens) == index - 1:
                print(f"Tokenizer: no tokens following after as!")
            identifier = tokens[index]
            if identifier in reserverd_tokens or identifier.isnumeric():
                print(
                    f"Tokenizer: {identifier} can't be used as identifier")
                sys.exit(-1)

            index += 1
            instruction = append_instruction(("store", identifier))
            continue
        else:
            append_instruction(("load", token))
            continue
    return instructions


def compile_sick_bytecode(src_name, binary_name):
    tokens = lex_file(src_name)
    instructions = tokens_to_instructions(tokens)

    def extract_params(params):
        if type(params) == tuple:
            mystr = ""
            for p in params:
                mystr += f" {p}"
            return mystr
        elif params == None:
            return ""
        return f" {params}"

    with open(binary_name + ".sickc", "w") as output_stream:
        output_stream.writelines(
            [f"{ins[0]}{extract_params(ins[1])}\n" for ins in instructions])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"OPPO Language - {oppo_version}")

    parser.add_argument("file", metavar="F", type=str, nargs=1,
                        help="File to compile")
    parser.add_argument("--compile", dest="compile",
                        choices=["sickvm"], type=str, required=False)
    parser.add_argument("--output", dest="output",
                        type=str, required=False)

    args = parser.parse_args()

    src_name = args.file[0]

    if args.compile != None:
        output_name = args.output if not None else "a"
        arch = args.compile
        if arch == "sickvm":
            compile_sick_bytecode(src_name, output_name)
        sys.exit(-1)

    tokens = lex_file("./example.oppo")
    instructions = tokens_to_instructions(tokens)
