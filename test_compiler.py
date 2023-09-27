from driver import compile_and_run
import numpy
import pytest
import math

# compresses a list for readability by collapsing runs of the same number into one element.
# For example: ["cheese","cheese","cheese","bread","bread","meat","cheese"] becomes [("cheese",3), ("bread",2), ("meat",1), ("cheese",1)]
def compress(array):
    result = []
    for n in array:
        if len(result) == 0 or result[-1][0] != n:
            result.append([n, 1])
        else:
            result[-1][1] += 1
    return [tuple(r) for r in result]

def run_and_test_program(program_string, answer):
    stack = compile_and_run(program_string)[0]
    print(compress(stack))
    if math.isnan(answer):
        assert numpy.any(numpy.isnan(stack))
    elif answer == math.inf:
        assert numpy.any(numpy.isinf(stack))
    else:
        assert numpy.any(abs(stack - answer) <= abs(answer) / 1000000) # Uses absolute value with offset to deal with floating point error

@pytest.mark.parametrize("program, answer", [
    ("addition", 10), # 3 + 7
    ("negative_addition", -9), # -4 + -5
    ("subtraction", -4), # 3 - 7
    ("multiplication", 21), # 3 * 7
    ("division", 0.42857142857), # 3 / 7
    ("division_by_zero", math.inf), # 3 / 0
    ("modulus", 5), # 19 % 7 
    ("modulus_fractional", 0.2), # 3 % 0.7
    ("modulus_by_zero", math.nan), # 3 % 0 
    ("power", 2187), # 3 ^ 7
    ("power_negative", 0.3333333333), # 3 ^ -1
    ("power_fractional", 1.97159185937), # 3.1 ^ 0.6
    ("power_nan", math.nan), # -1 ^ 0.5
])
def test_math_operations(program, answer):
    run_and_test_program(f"test_files/math_operations/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
    ("basic_function", 8),
    ("naked_function", 8),
    ("variable_function", 13),
    ("function_with_assign", 14),
    ("two_variable_function", 8),
    ("two_variable_function_with_assign", 10),
    ("many_variable_function", 350),
    ("several_functions", 15),
    ("nested_functions", 15),
    ("nested_functions_with_variables", 41),
    ("builtin_function", math.sin(1))
])
def test_functions(program, answer):
    run_and_test_program(f"test_files/functions/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
    ("basic_construct", 49),
    ("construct_with_reassign", 49),
    ("construct_with_self_assign", 81),
    ("construct_with_many_assigns", 49),
    ("tangled_construct", -18),
    ("long_variable",  49),
    ("empty_construct",  49),
    ("empty_construct_pause",  49),
])
def test_variables(program, answer):
    run_and_test_program(f"test_files/variables/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
    ("basic_if", 9),
    ("basic_if_false", 5),
    ("if_five", 9),
    ("basic_else", 5),
    ("basic_else_false", 9),
    ("else_if_true", 9),
    ("else_if_false", 5),
    ("else_if_shortcircuit", 5),
    ("else_if_long", 9),
    ("nested_if", 9),
])
def test_if_and_else(program, answer):
    run_and_test_program(f"test_files/if_and_else/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
    ("basic_while", 11),
    ("skipped_while", 11),
    ("nested_while", 32),
    ("basic_for", 1025),
    ("for_as_while", 1025),
    ("skipped_for", 3),
    ("nested_for", 100),
])
def test_for_and_while(program, answer):
    run_and_test_program(f"test_files/for_and_while/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
    ("external", math.pi / 2 + 1), # pi/2 plus 1
    ("two_externals", (1 + 5 ** 0.5) / 2 * math.pi / 2), # golden ratio * pi/2
    ("external_assign", 5),
])
def test_externals(program, answer):
    run_and_test_program(f"test_files/externals/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
    ("basic_pointer", 7),
    ("double_pointer", 7),
    ("assign_to_pointer", 9),
    ("pointer_assign", 9),
    ("double_pointer_assign", 9),
    ("assign_to_pointer_through_pointer", 9),
    ("function_with_pointer_assign", 10),
    ("double_pointer_assign_in_function", 10),
])
def test_pointers(program, answer):
    run_and_test_program(f"test_files/pointers/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
    ("basic_array", 105),
    ("one_element_array", 8),
    ("long_array", 129),
    ("modified_array", -777),
    ("multidimensional_array", 11),
    ("multidimensional_array_split", 11),
    ("multidimensional_array_assign", 11),
    ("multidimensional_array_split_assign", 11),
    ("multidimensional_array_with_for_loops", 21),
    ("array_assign", 105),
    ("second_array_assign", 105),
    ("pointer_to_array", 6),
    ("double_pointer_to_array", 6),
    ("unassigned_array", -777),
    ("unassigned_array_double", 193),
])
def test_arrays(program, answer):
    run_and_test_program(f"test_files/arrays/{program}.bc", answer)

@pytest.mark.parametrize("program, answer", [
   ("prime_count", 25), # count of primes up to 100
   ("prime_count_functional", 25), # count of primes up to 100
   ("pentagonal_numbers", 92), # see test file
   ("squbes", 432), # see test file
])
def test_integration(program, answer):
   run_and_test_program(f"test_files/integration/{program}.bc", answer)

# For running individual tests without pytest and with more control
def debug():
    program_string = f"test_files/integration/prime_count_functional.bc"
    stack = compile_and_run(program_string, threads=1, blocks=1)[0]
    print(compress(stack))
    assert numpy.any(abs(stack - 49) <= abs(49) / 1000000)

if __name__ == "__main__":
    debug()