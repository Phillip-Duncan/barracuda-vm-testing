from driver import compile_and_run
import numpy
import pytest

# Paramtererized tests for operations
@pytest.mark.parametrize("program, answer", [
    ("addition", 10), # test 3 + 7 is 10
    ("multiplication", 21), # test 3 * 7 is 21
])
def test_operation(program, answer):
    program_string = f"test_files/{program}.bc"
    stack = compile_and_run(program_string)[0]
    assert numpy.any(stack == answer)