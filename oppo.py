oppo_version = "0.0.1"
stack = []


def lex_file(file_path: str):
    with open(file_path, "r") as file:
        return lex_lines(file.readlines())


def lex_lines(lines: str):
    tokens = []

    for line in lines:
        splitted = line.strip().split(" ")
        if len(splitted) == 1 and splitted[0] == "":
            continue
        for token in splitted:
            if token == "#":
                break
            tokens.append(token)
    return tokens


def tokens_to_instructions(tokens):
    instructions = []
    for token in tokens:
        if token.isnumeric():
            instructions.append(("push", int(token)))
        elif token == "+":
            instructions.append(("plus", ))
        elif token == "-":
            instructions.append(("sub", ))
        elif token == "~":
            instructions.append(("print", ))
        else:
            print(f"Unknown symbol: {token}")
    return instructions


def interpret_instructions(instructions):
    for i in range(len(instructions)):
        instruction = instructions[i]
        op = instruction[0]
        if op == "push":
            val = instruction[1]
            exec_push(val)
        elif op == "plus":
            exec_plus()
        elif op == "sub":
            exec_sub()
        elif op == "print":
            exec_print()


def exec_push(num: int):
    stack.append(num)


def exec_plus():
    result = int(stack.pop()) + int(stack.pop())
    exec_push(result)


def exec_sub():
    result = int(stack.pop()) - int(stack.pop())
    exec_push(result)


def exec_print():
    tail = stack[len(stack) - 1]
    print(tail)


if __name__ == "__main__":
    print(f"OPPO Language - {oppo_version}")
    tokens = lex_file("./example.oppo")
    instructions = tokens_to_instructions(tokens)

    interpret_instructions(instructions)
