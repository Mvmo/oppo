import argparse
import sys

from tokenizer import *
from typing import *

oppo_version = "0.0.1"

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def remove_suffix(text, suffix):
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text

def tokens_to_instructions(tokens):
    instructions = []
    stack = []

    def append_instruction(x: tuple):
        instructions.append(
            (x[0], x[1] if len(x) == 2 else None, len(instructions)))
        return x

    index = 0
    while index < len(tokens):
        token: Token = tokens[index]
        ri = len(instructions)
        index += 1
        if token.typ == TokenType.INT:
            append_instruction(("ipush", int(token.literal)))
        if token.typ == TokenType.BOOLEAN:
            append_instruction(("bpush", token.literal.lower()))
        if token.typ == TokenType.STRING:
            append_instruction(("spush", token.literal))
        if token.typ == TokenType.INTRINSIC:
            literal = token.literal
            if literal == "+":
                append_instruction(("add", ))
            elif literal == "-":
                append_instruction(("sub", ))
            elif literal == "*":
                append_instruction(("mul", ))
            elif literal == "/":
                append_instruction(("div", ))
            elif literal == "~":
                append_instruction(("dump", ))
            elif literal == "=":
                append_instruction(("cmp", ))
            elif literal == "<":
                append_instruction(("lt", ))
            elif literal == "<=":
                append_instruction(("lte", ))
            elif literal == ">":
                append_instruction(("gt", ))
            elif literal == ">=":
                append_instruction(("gte", ))
            elif literal == "dup":
                append_instruction(("dup", ))
            elif literal == "print":
                append_instruction(("print", ))
            elif literal == "println":
                append_instruction(("println", ))
            elif literal == "if":
                instruction = append_instruction(("cjmp", ("if", ri)))
                stack.append(instruction)
                # first param is where to jump if true and end param is where to jmp if false
            elif literal == "else":
                enclosing = stack.pop()
                if_index = enclosing[1][1]

                instructions[if_index] = ("cjmp", (if_index + 1, ri + 1))
                instruction = append_instruction(("jmp", ("else", ri)))
                stack.append(instruction)
            elif literal == "while":
                instruction = append_instruction((f"$~while{len(instructions)}:", ))
                stack.append(instruction)
            elif literal == "do":
                enclosing = stack.pop()
                instruction = append_instruction(("cjmp", ("do", enclosing[0], ri)))
                stack.append(instruction)
            elif literal == "end":
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
                    append_instruction((remove_suffix(f"goto {while_label}", ":"), ))
            elif literal == "as":
                if len(tokens) == index - 1:
                    print(f"Tokenizer: no tokens following after as!")
                identifier = tokens[index].literal
                if identifier in intrinsics or identifier.isnumeric():
                    print(f"Tokenizer: {identifier} can't be used as identifier")
                    sys.exit(-1)

                index += 1
                instruction = append_instruction(("store", identifier))
                continue
        elif token.typ == TokenType.IDENTIFIER:
            append_instruction(("load", token.literal))
            continue
    return instructions


def compile_instructions_to_sickvm(instructions, binary_name):
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
    parser = argparse.ArgumentParser(description=f"OPPO Language - {oppo_version}")

    parser.add_argument("file", metavar="F", type=str, nargs=1, help="File to compile")
    parser.add_argument("--compile", dest="compile", choices=["sickvm"], type=str, required=False)
    parser.add_argument("--output", dest="output", type=str, required=False)
    parser.add_argument("--debug", dest="debug", type=bool, required=False)

    args = parser.parse_args()
    src_name = args.file[0]

    tokens: "list[Token]" = None
    with open(src_name, "r") as file:
        tokens = tokenize(file.read(), debug = args.debug)

    instructions = tokens_to_instructions(tokens)

    if args.compile != None:
        output_name = args.output if not None else "a"
        arch = args.compile
        if arch == "sickvm":
            compile_instructions_to_sickvm(instructions, output_name)
        else:
            sys.exit(-1)
