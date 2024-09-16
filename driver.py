from compiler import *
import ctypes
from numpy.ctypeslib import ndpointer


def compile_and_run(program, precision: int = 1, threads: int = 128, blocks: int = 8):
    osname = sys.platform.upper()

    library_str = 'vm/'
    if "LINUX" in osname:
        solver = ctypes.CDLL(f'{library_str}libvm_generic.so')
    elif "WIN" in osname:
        solver = ctypes.CDLL(f'{library_str}vm_generic.dll')
    else:
        print("Cannot detect OS... Assuming unknown linux distribution")
        solver = ctypes.CDLL(f'{library_str}libvm_generic.so')

    # shorthand memory defintions
    CTF = "C_CONTIGUOUS"
    double_ptr = ndpointer(ctypes.c_double, flags=CTF)  # type: ignore # noqa: F841
    float_ptr = ndpointer(ctypes.c_float, flags=CTF)  # type: ignore
    int_ptr = ndpointer(ctypes.c_int32, flags=CTF)  # type: ignore
    short_ptr = ndpointer(ctypes.c_short, flags=CTF)
    long_ptr = ndpointer(ctypes.c_long, flags=CTF)  # type: ignore # noqa: F841
    longlong_ptr = ndpointer(ctypes.c_longlong, flags=CTF)  # type: ignore

    bc = Barracuda(precision = int(precision * 32))
    bc.load(program)

    user_space = numpy.array([])

    instr_stack = bc.instructions
    op_stack = bc.operations
    value_stack = bc.values
    sizes = bc.sizes

    result = numpy.zeros(sizes[3] * threads * blocks, dtype=ctypes.c_double)

    if precision == 1:
        solve_func = solver.solve_32
        solve_func.restype = None
        solve_func.argtypes = [int_ptr, longlong_ptr, double_ptr, ctypes.c_int32, ctypes.c_int32,
                               double_ptr, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, double_ptr]
        solve_func(instr_stack, op_stack, value_stack, sizes[0], sizes[3], user_space, sizes[4], blocks, threads,
                   result)
    elif precision == 2:
        solve_func = solver.solve_64
        solve_func.restype = None
        solve_func.argtypes = [int_ptr, longlong_ptr, double_ptr, ctypes.c_int32, ctypes.c_int32,
                               double_ptr, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, double_ptr]
        solve_func(instr_stack, op_stack, value_stack, sizes[0], sizes[3], user_space, sizes[4], blocks, threads,
                   result)

    return result, bc
