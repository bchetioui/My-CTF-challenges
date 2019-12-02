#!/usr/bin/python3
from tempfile import NamedTemporaryFile
import os
import random
import re
import signal
import subprocess
import sys

def handler(signum, frame):
    exit_fail('Bye bye!~')

def exit_fail(message='Nope!'):
    print(message)
    exit(1)

def gen_tactic_line(command, operandes):
    return command.format(*operandes)

def parse_solution(encoded_solution):
    tactics = { '00': 'intros.',
                '01': 'intro.',
                '02': 'induction {}.',
                '03': 'reflexivity.',
                '04': 'rewrite {}.',
                '05': 'rewrite <- {}.',
                '06': 'simpl.' }

    identifiers = re.compile(r'[A-Za-z0-9_]+', re.S)
    try:
        solution_lines = bytes.fromhex(encoded_solution).decode('utf-8').split('\n')
        solution = '\n'.join([tactics[l[:2]].format(*list(identifiers.findall(l[2:]))) for l in solution_lines])
        return solution
    except:
        exit_fail()

def solve(problem, solution):
    try:
        v_file_content = problem + '\nProof.\n' + solution + '\nQed.'

        sourcefile = NamedTemporaryFile(suffix='.v', delete=False)
        sourcefile.write(v_file_content.encode('ascii'))
        sourcefile.close()

        result = subprocess.run(['coqc', sourcefile.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

        os.unlink(sourcefile.name)

        return result
    except:
        exit_fail()

def get_new_problem(problems):
    return random.choice(problems)

def new_stack(problems, stack=[]):
    stack.append(get_new_problem(problems))
    return stack

def undo(stack, index):
    if index % len(stack) == 0:
        return index
    return index - 1

def redo(index):
    if index == -1:
        return -1
    return index + 1

def print_menu(passes_allowed):
    print('1. Solve problem')
    print('2. Get back to previous problem in stack')
    print('3. Get back to next problem in stack')
    if passes_allowed > 0:
        print('4. This problem is too hard, give me a new problem!')

def main():
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(60)

    passes = 3
    lemmas = []
    with open('lemmas.txt', encoding='UTF-8') as f:
        lemmas = list(filter(lambda lemma: lemma != '', f.read().split('\n')))

    print('Welcome to the Coq experience!')
    print('Solve 100 problems and get a flag!')

    for count in range(100):
        stack = new_stack(lemmas)
        stack_index = -1
        while 1:
            print('Problem is {}'.format(stack[stack_index]))
            print_menu(passes)
            try:
                choice = int(input())
            except:
                exit()
            if choice == 1:
                solution = parse_solution(input('OK, give me your solution: '))
                if solve(stack[stack_index], solution):
                    break
                else:
                    exit_fail()

            elif choice == 2:
                stack_index = undo(stack, stack_index)
            elif choice == 3:
                stack_index = redo(stack_index)
            elif passes > 0 and choice == 4:
                stack.append(get_new_problem(lemmas))
                stack_index = -1
                passes -= 1
            else:
                exit_fail()
    
    print('Well played, you\'re the Coq master!')
    with open('flag.txt') as f:
        print(f.read())

if __name__ == '__main__':
    main()
