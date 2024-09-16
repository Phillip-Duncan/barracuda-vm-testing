import numpy as np
import struct

# Packs a string into an array of 64-bit floating point numbers.
def pack_string_to_f64_array(s: str) -> np.ndarray:
    # Ensure the string is a multiple of 8 by padding with '\0' if needed
    padded_string = s + '\0' * (8 - len(s) % 8) if len(s) % 8 != 0 else s
    
    float_array = []
    
    # Iterate over the string in chunks of 8 characters
    for i in range(0, len(padded_string), 8):
        chunk = padded_string[i:i+8]
        
        # Convert the 8 characters into a little-endian 64-bit integer
        packed_int = int.from_bytes(chunk.encode('ascii'), byteorder='little')
        
        # Now interpret the integer as a float64
        packed_float = struct.unpack('<d', struct.pack('<Q', packed_int))[0]
        
        # Append to the float array
        float_array.append(packed_float)
    
    return np.array(float_array, dtype=np.float64)