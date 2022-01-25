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

    def append_instruction(x: tuple, array=instructions):
        instructions.append(
            (x[0], x[1] if len(x) == 2 else None, len(instructions)))

    def find_end_or_else(start):
        for _index in range(start, len(tokens)):
            token = tokens[_index]
            if token != "end" and token != "else":
                continue
            return (_index, token)

    for index in range(len(tokens)):
        token = tokens[index]
        if token.isnumeric():
            append_instruction(("push", int(token)))
        elif token == "+":
            append_instruction(("plus", ))
        elif token == "-":
            append_instruction(("sub", ))
        elif token == "~":
            append_instruction(("print", ))
        elif token == "=":
            append_instruction(("cmp", ))
        elif token == "if":
            start_index = index + 1
            end = find_end_or_else(index)

            end_index = end[0]

            if end[1] == "else":
                end_index = end_index + 1

            # first param is where to jump if true and end param is where to jmp if false
            append_instruction(("cjmp", (start_index, end_index)))
        elif token == "else":
            end = find_end_or_else(index + 1)
            append_instruction(("jmp", end[0]))
        elif token == "end":
            continue
        else:
            print(f"Unknown symbol: {token}")
    return instructions


def interpret_instructions(instructions):
    index_iter = iter(range(len(instructions)))
    for i in index_iter:
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
        elif op == "cmp":
            exec_compare()
        elif op == "cjmp":
            points = instruction[1]
            where_to_jump = exec_conditional_jump(points[0], points[1])
            for _ in range(where_to_jump - i - 1):
                next(index_iter)
        elif op == "jmp":
            point = instruction[1]
            for _ in range(point - i - 1):
                next(index_iter)


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


def exec_compare():
    stack.append(int(stack.pop() == stack.pop()))


def exec_conditional_jump(if_true: int, if_false: int):
    condition = stack.pop()
    return if_true if bool(condition) else if_false


if __name__ == "__main__":
    print(f"OPPO Language - {oppo_version}")
    tokens = lex_file("./example.oppo")
    instructions = tokens_to_instructions(tokens)

    # for x in instructions:
    #  print(x)

    interpret_instructions(instructions)
