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

# Paramtererized tests for mathematical operations
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
def test_operation(program, answer):
    program_string = f"test_files/math_operations/{program}.bc"
    stack = compile_and_run(program_string)[0]
    print(compress(stack))
    if math.isnan(answer):
        assert numpy.any(numpy.isnan(stack))
    elif answer == math.inf:
        assert numpy.any(numpy.isinf(stack))
    else:
        assert numpy.any(abs(stack - answer) <= abs(answer) / 1000000) # Uses absolute value with offset to deal with floating point error