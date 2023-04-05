from driver import compile_and_run

#Runs a program and then checks that a specific value appears in the stack.
def is_value_in_stack(program, answer):
    for value in compile_and_run(program):
        if value == answer:
            print(value, answer)
            return True
    return False

# Tests 3 + 7 returns 10.
def test_addition():
    assert is_value_in_stack("test_addition.bc", 10)

# Tests 3 * 7 returns 21.
def test_multiplication():
    assert is_value_in_stack("test_multiplication.bc", 21)
