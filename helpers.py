from typing import List
import struct

def pack_string_to_f64_array(input: str, precision: int = 64) -> List[float]:
    result = []
    bytes_data = input.encode('utf-8')

    if precision == 32:
        chunk_size = 4  # 4 bytes for 32-bit precision
    elif precision == 64:
        chunk_size = 8  # 8 bytes for 64-bit precision
    else:
        raise ValueError(f"Unsupported precision: {precision}")

    for i in range(0, len(bytes_data), chunk_size):
        chunk = bytes_data[i:i + chunk_size]
        packed = 0
        for j, byte in enumerate(chunk):
            packed |= byte << (j * 8)

        # Shift the packed value to the left to fill the remaining bits with 0s
        packed <<= 8 * (chunk_size - len(chunk))

        if precision == 32:
            packed_bytes = packed.to_bytes(4, byteorder='little')
            float_value = struct.unpack('<f', packed_bytes)[0]
            result.append(float(float_value))  # Convert to float64
        elif precision == 64:
            packed_bytes = packed.to_bytes(8, byteorder='little')
            float_value = struct.unpack('<d', packed_bytes)[0]
            result.append(float_value)
        else:
            # This point should not be reached due to the earlier check
            pass

    return result