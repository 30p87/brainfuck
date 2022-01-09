from argparse import ArgumentParser
from sys import maxsize
from ast import literal_eval as to_list


def main(program, pointer=0, instruction_pointer=0, max_int=maxsize, max_cells=maxsize, input_buffer=None, loops=None, memory=None):
    def try_convert(_val, _type, _name):
        if type(_val) != _type:
            try:
                _r = to_list(_val)
            except SyntaxError:
                raise SyntaxError(f"Input value of {_name} must be a {_type.__name__}. Use -h to get help.")
            except ValueError:
                raise SyntaxError(f"Input value of {_name} must be a {_type.__name__}. Use -h to get help.")
            return _r
        else:
            return _val

    input_buffer = try_convert(input_buffer, list, "input_buffer")
    loops = try_convert(loops, dict, "loops")
    memory = try_convert(memory, dict, "memory")

    if input_buffer is None:
        input_buffer = []
    if loops is None:
        loops = {}
    if memory is None:
        memory = {0: 0}
    if program.endswith(".bf"):
        try:
            _file = open(program)
            program = _file.read()
            _file.close()
        except FileNotFoundError:
            pass

    if len(program) < 1:
        exit()

    program = list(program.replace("\n", ""))

    def process_loop(_start, _end):
        for _instruction_pointer in range(_start, _end):
            if program[_instruction_pointer] == "[":
                in_loop = 1
                _start = _instruction_pointer
                for i in range(_instruction_pointer + 1, len(program)):
                    if program[i] == "[":
                        in_loop += 1
                    elif program[i] == "]":
                        in_loop -= 1
                    if in_loop == 0:
                        loops[_instruction_pointer] = i
                        process_loop(_instruction_pointer + 1, i)
                        break
                process_loop(i, _end)
                break

    print("preprocessing loops")
    process_loop(0, len(program))

    while True:
        if program[instruction_pointer] == ">":
            pointer += 1
            if pointer > max_cells:
                pointer = 0
            try:
                memory[pointer]
            except KeyError:
                memory[pointer] = 0
        elif program[instruction_pointer] == "<":
            pointer -= 1
            if pointer < 0:
                pointer = max_cells
            try:
                memory[pointer]
            except KeyError:
                memory[pointer] = 0
        elif program[instruction_pointer] == "+":
            memory[pointer] += 1
            if memory[pointer] > max_int:
                memory[pointer] = 0
        elif program[instruction_pointer] == "-":
            memory[pointer] -= 1
            if memory[pointer] < 0:
                memory[pointer] = max_int
        elif program[instruction_pointer] == ".":
            print(chr(memory[pointer]), end="")
        elif program[instruction_pointer] == ",":
            if len(input_buffer) < 1:
                input_buffer += list(input())
            memory[pointer] = ord(input_buffer[0])
            input_buffer.pop(0)
        elif program[instruction_pointer] == "[":
            if memory[pointer] == 0:
                instruction_pointer = loops[instruction_pointer]
        elif program[instruction_pointer] == "]":
            instruction_pointer = list(loops.keys())[list(loops.values()).index(instruction_pointer)] - 1

        instruction_pointer += 1
        if instruction_pointer == len(program):
            print()
            break


if __name__ == "__main__":
    argparser = ArgumentParser(description="A simple brainfuck interpreter.")
    argparser.add_argument("program", help="The program to execute. Can also be the path to a .bf file.", type=str)
    argparser.add_argument("--max_int",
                           help="The maximum size of an integer, or the value of a cell, before it loops back to 0.",
                           default=maxsize, type=int, required=False)
    argparser.add_argument("--max_cells", help="The maximum number of cells, before the pointer loops back to 0.",
                           default=maxsize, type=int, required=False)
    argparser.add_argument("--pointer", help="Where the memory pointer should start.", default=0, type=int,
                           required=False)
    argparser.add_argument("--instruction_pointer", help="Where the memory pointer should start.", default=0, type=int,
                           required=False)
    argparser.add_argument("--input_buffer", help="How the input buffer, aka. a storage so you can enter multiple inputs at once and let the program handle it, should look like.", default="[]", type=str,
                           required=False)
    argparser.add_argument("--memory", help="How the memory should look before executing, useful for large programs "
                                            "which require preset values, eg. specific characters.", default="{0: 0}",
                           type=str, required=False)
    argparser.add_argument("--loops",
                           help="How the internal loop index should look before executing, not useful at all "
                                "cuz the program generates it itself lol.", default="{}", type=str, required=False)
    args = argparser.parse_args()
    main(args.program, args.pointer, args.instruction_pointer, args.max_int, args.max_cells, args.input_buffer, args.loops, args.memory)
