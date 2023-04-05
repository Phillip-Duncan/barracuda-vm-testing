import numpy
import ctypes
import sys
import os
import threading

_c_float_p = ctypes.POINTER(ctypes.c_double)
_c_uint32_p = ctypes.POINTER(ctypes.c_uint32)
_c_uint64_p = ctypes.POINTER(ctypes.c_uint64)


class _Vec_uint32_t(ctypes.Structure):
    _fields_ = (("ptr", _c_uint32_p),
                ("len", ctypes.c_size_t),
                ("cap", ctypes.c_size_t),)


class _Vec_uint64_t(ctypes.Structure):
    _fields_ = (("ptr", _c_uint64_p),
                ("len", ctypes.c_size_t),
                ("cap", ctypes.c_size_t),)


class _Vec_float_t(ctypes.Structure):
    _fields_ = (("ptr", _c_float_p),
                ("len", ctypes.c_size_t),
                ("cap", ctypes.c_size_t),)


class _EnvironmentVariable(ctypes.Structure):
    _fields_ = (("identifier", ctypes.c_char_p),
                ("ptr_offset", ctypes.c_size_t),
                ("datatype", ctypes.c_char_p),
                ("qualifier", ctypes.c_char_p)
                )


class _Vec_EnvironmentVariable_t(ctypes.Structure):
    _fields_ = (("ptr", ctypes.POINTER(_EnvironmentVariable)),
                ("len", ctypes.c_size_t),
                ("cap", ctypes.c_size_t),)


class _CompilerResponse(ctypes.Structure):
    _fields_ = (("code_text", ctypes.c_char_p),
                ("instructions_list", _Vec_uint32_t),
                ("operations_list", _Vec_uint64_t),
                ("values_list", _Vec_float_t),
                ("recommended_stack_size", ctypes.c_size_t)
                )


class _CompilerRequest(ctypes.Structure):
    _fields_ = (("code_text", ctypes.c_char_p),
                ("env_vars", _Vec_EnvironmentVariable_t),
                )


class Barracuda:
    def __init__(self, lib_dir: str = '', env_cfg_dir: str = ''):
        """Initialises Barracuda object for compilation of Barracuda scripts into bytecode arrays.

        Args:
            lib_dir: library directory where barracuda_compiler shared library is located. (e.g, C:/bcc_lib/),
            defaults to compiler included in package install location.
        """
        if not lib_dir:
            self.lib_dir = f'{os.path.dirname(os.path.realpath(__file__))}/compiler'
        else:
            self.lib_dir = lib_dir

        if not env_cfg_dir:
            self.env_cfg_dir = f'{os.path.dirname(os.path.realpath(__file__))}'
        else:
            self.env_cfg_dir = env_cfg_dir

        self.compiler = None

        self.osname = sys.platform.upper()

        self.instructions: numpy.typing.NDArray[numpy.int32] = numpy.array([], dtype=numpy.int32)
        self.values: numpy.typing.NDArray[numpy.float64] = numpy.array([], dtype=numpy.float64)
        self.operations: numpy.typing.NDArray[numpy.int64] = numpy.array([], dtype=numpy.int64)

        self.sizes: numpy.typing.NDArray[numpy.int32] = numpy.zeros(5, dtype=numpy.int32)

        # self.stack_size: int = 0

    def read_environment_config(self, file):
        if file == '':
            raise IOError(f'File not specified')

        env_vars = []

        with open(file, 'r') as f:
            ftext = f.read()

        parsed_text = ftext.replace('\t', '').splitlines()

        for (i, line) in enumerate(parsed_text):
            var = line.split(':')

            if len(var) == 4:
                new_env = _EnvironmentVariable()
                new_env.ptr_offset = ctypes.c_size_t(int(var[0]))
                new_env.identifier = ctypes.c_char_p(var[1].encode('utf-8'))
                new_env.datatype = ctypes.c_char_p(var[2].encode('utf-8'))
                new_env.qualifier = ctypes.c_char_p(var[3].encode('utf-8'))

                env_vars.append(new_env)
            else:
                continue

        elems = (_EnvironmentVariable * len(env_vars))()
        struct_array = ctypes.cast(elems, ctypes.POINTER(_EnvironmentVariable))

        for j in range(0, len(env_vars)):
            struct_array[j] = env_vars[j]

        env_vars_vec = _Vec_EnvironmentVariable_t()

        env_vars_vec.ptr = struct_array
        env_vars_vec.len = ctypes.c_size_t(len(env_vars))
        env_vars_vec.cap = ctypes.c_size_t(len(env_vars))

        return env_vars_vec

    def preprocess(self, file):
        keyword = "#import"

        included_files = []

        ftext = ''
        with open(file, 'r') as f:
            ftext = f.read()
            included_files.append(file)

        parsed_text = ftext.replace('\t', '').splitlines()

        while True:
            includes = []
            for (i, line) in enumerate(parsed_text):
                if keyword in line:
                    incl_filepath = line.replace(keyword, '').replace(' ', '').replace('"', '')
                    includes.append(i)
                    includes.append(incl_filepath)

                    with open(incl_filepath, 'r') as f_i:
                        if incl_filepath not in included_files:
                            f_itext = f_i.read().replace('\t', '').splitlines()
                            parsed_text.pop(i)
                            parsed_text[i:i] = f_itext

                            included_files.append(incl_filepath)
                        else:
                            print(f"File {incl_filepath=} already imported.")
            if not includes:
                break

        return "\n".join(parsed_text)

    def call_compiler(self, code, env_vars, output):
        if self.compiler is None:
            raise ValueError(f'Cannot compile Barracuda program as compiler not set. {self.compiler=}')

        # call compiler to compile parsed code
        compile_func = self.compiler.compile
        compile_func.restype = _CompilerResponse
        compile_func.argtypes = [ctypes.POINTER(_CompilerRequest)]

        bc_string = code.encode('utf-8')
        code_ptr = ctypes.c_char_p(bc_string)

        c_req = _CompilerRequest(code_ptr, env_vars)
        c_req_ptr = ctypes.pointer(c_req)

        output.append(compile_func(c_req_ptr))

    def load(self, file):
        """

        Load barracuda file containing barracuda code.

        Args:
            file: path to barracuda file.

        Returns: Barracuda object with arrays filled with instructions, values, operations and size.

        """
        library_str = f'{self.lib_dir}/'
        if "LINUX" in self.osname:
            self.compiler = ctypes.CDLL(f'{library_str}libbarracuda_compiler.so', winmode=0)
        elif "WIN" in self.osname:
            self.compiler = ctypes.CDLL(f'{library_str}barracuda_compiler.dll', winmode=0)
        else:
            print("Cannot detect OS... Assuming unknown linux distribution")
            self.compiler = ctypes.CDLL(f'{library_str}libbarracuda_compiler.so', winmode=0)

        # pre-process imports, etc from file(s)
        code = self.preprocess(file)

        env_vars = self.read_environment_config(f'{self.env_cfg_dir}/env_vars.cfg')

        out = []
        try:
            # compiled_output = compile_func(c_req_ptr)
            x = threading.Thread(target=self.call_compiler(code, env_vars, out), args=(2,), daemon=True)
            x.start()
            x.join()
        except Exception as e:
            print(e)

        compiled_output = out[0]

        self.instructions = numpy.ctypeslib.as_array(compiled_output.instructions_list.ptr,
                                                     shape=(compiled_output.instructions_list.cap,)).astype(numpy.int32)

        self.operations = numpy.ctypeslib.as_array(compiled_output.operations_list.ptr,
                                                   shape=(compiled_output.operations_list.cap,)).astype(numpy.int64)

        self.values = numpy.ctypeslib.as_array(compiled_output.values_list.ptr,
                                               shape=(compiled_output.values_list.cap,))  # .astype(numpy.float64)

        self.instructions = numpy.concatenate(([0], self.instructions)).astype(numpy.int32)
        self.values = numpy.concatenate(([0], self.values))
        self.operations = numpy.concatenate(([0], self.operations))

        stack_size = int(compiled_output.recommended_stack_size)

        self.sizes = numpy.array([self.instructions.size, self.operations.size, self.values.size, stack_size, 0],
                                 dtype=numpy.int32)

        return self
