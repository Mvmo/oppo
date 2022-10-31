import argparse
from cgi import print_form
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

def tokens_to_instructions(tokens: "list[Token]", include_array: "list[str]" = []) -> list:
    files_to_include = list(
                filter(lambda file_name : not file_name in include_array,
                map(lambda token : token.literal, 
                filter(lambda token : token.typ == TokenType.INCLUDE, tokens))))

    for file_name in files_to_include:
        with open(file_name + ".oppo", "r") as file:
            include_array.append(file_name)
            tokens += tokenize(file.read())

    if len(files_to_include) >= 1:
        return tokens_to_instructions(tokens)

    tokens = list(filter(lambda token : token.typ != TokenType.INCLUDE, tokens))

    function_names = []
    for i in range(len(tokens)):
        token = tokens[i]
        if token.typ == TokenType.KEYWORD and token.literal == "proc":
            function_names.append(tokens[i+1].literal)

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
        literal = token.literal
        if token.typ == TokenType.INT:
            append_instruction(("ipush", int(token.literal)))
        if token.typ == TokenType.BOOLEAN:
            append_instruction(("bpush", token.literal.lower()))
        if token.typ == TokenType.STRING:
            append_instruction(("spush", token.literal))
        if token.typ == TokenType.INTRINSIC:
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
            elif literal == "sizeof":
                append_instruction(("sizeof", ))
            elif literal == "swap":
                append_instruction(("swap", ))
            elif literal == "dup":
                append_instruction(("dup", ))
            elif literal == "print":
                append_instruction(("print", ))
            elif literal == "println":
                append_instruction(("println", ))
        elif token.typ == TokenType.KEYWORD:
            if literal == "if":
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
            elif literal == "proc":
                if len(tokens) == index - 1:
                    print(f"Tokenizer: no tokens following after as!")
                    sys.exit(1)
                identifier = tokens[index].literal
                if identifier in intrinsics or identifier in keywords or identifier.isnumeric():
                    print(f"Tokenizer: {identifier} can't be used as identifier")
                    sys.exit(1)

                index += 1

                jmp_instruction = append_instruction(("jmp", ("proc_start", ri)))
                append_instruction((f"{identifier}:", ))

                params = []
                next_token = tokens[index]
                while next_token.literal != "do":
                    if next_token.typ != TokenType.TYPE:
                        print(f"Expected type and got {next_token.typ}")
                        sys.exit(-1)

                    type_name = next_token.literal
                    
                    index = index + 1
                    next_token = tokens[index]

                    if next_token.typ != TokenType.IDENTIFIER:
                        print(f"Expected identififer and got {next_token.typ}")
                        sys.exit(-1)

                    params.append((type_name, next_token.literal))

                    index = index + 1
                    next_token = tokens[index]
                
                for param in reversed(params):
                    append_instruction(("req", (param[0])))
                    append_instruction(("store", (param[1])))

                jmp_instruction = ("jmp", ("proc_start", ri, params))

                stack.append(jmp_instruction)
                instructions[jmp_instruction[1][1]] = jmp_instruction

                index += 1
            elif literal == "do":
                if len(stack) == 0:
                    continue
                enclosing = stack[len(stack) - 1]
                if not str(enclosing[0]).startswith("$~while"):
                    print(f"continue")
                    continue
                stack.pop()
                instruction = append_instruction(("cjmp", ("do", enclosing[0], ri)))
                stack.append(instruction)
            elif literal == "end":
                enclosing = stack.pop()
                typ = enclosing[1][0]
                if typ == "if":
                    if_index = enclosing[1][1]
                    instructions[if_index] = (
                        "cjmp", (if_index + 1, ri))
                elif typ == "else":
                    else_index = enclosing[1][1]
                    instructions[else_index] = ("jmp", (ri))
                elif typ == "do":
                    while_label = enclosing[1][1]
                    do_index = enclosing[1][2]
                    instructions[do_index] = ("cjmp", (do_index + 1, ri + 1))
                    append_instruction((remove_suffix(f"goto {while_label}", ":"), ))
                elif typ == "proc_start":
                    jmp_index = enclosing[1][1]
                    identififers_to_del = enclosing[1][2]
                    for identififer in identififers_to_del:
                        append_instruction(("del", identififer[1]))
                    append_instruction(("goto", "$"))
                    instructions[jmp_index] = ("jmp", len(instructions))
            elif literal == "as":
                if len(tokens) == index - 1:
                    print(f"Tokenizer: no tokens following after as!")
                identifier = tokens[index].literal
                if identifier in intrinsics or identifier in keywords or identifier.isnumeric():
                    print(f"Tokenizer: {identifier} can't be used as identifier")
                    sys.exit(-1)

                index += 1
                instruction = append_instruction(("store", identifier))
                continue
        elif token.typ == TokenType.IDENTIFIER:
            if token.literal in function_names:
                append_instruction(("call", token.literal))
                continue
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
    parser = argparse.ArgumentParser(description=f"OPPO Compiler - {oppo_version}")

    parser.add_argument("file", metavar="F", type=str, nargs=1, help="File to compile")
    parser.add_argument("--target", dest="target", choices=["sickvm"], type=str, required=False)
    parser.add_argument("--output", dest="output", type=str, required=False)
    parser.add_argument("--debug", dest="debug", type=bool, required=False)

    args = parser.parse_args()
    src_name = args.file[0]

    tokens: "list[Token]" = None
    with open(src_name, "r") as file:
        tokens = tokenize(file.read(), debug = args.debug)

    instructions = tokens_to_instructions(tokens)

    if args.target != None:
        output_name = args.output if not None else "a"
        target = args.target
        if target == "sickvm":
            compile_instructions_to_sickvm(instructions, output_name)
    else:
        print(f"You need to specify a target architecture [sickvm]")
