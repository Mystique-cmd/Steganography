import struct
def read_bmp_bytes(path):
    with open(path , "rb") as f:
        return f.read()

def write_bmp_bytes(path, data):
    with open (path, "wb") as f:
        f.write(data)

def parse_bmp_header(b):
    if len(b) < 54:
        raise ValueError("Not a valid BMP(too small)")
    if b[0:2] != b'BM':
        raise ValueError("Not a BMP file (missing BM header)")
    file_size = struct.unpack_from("<I", b, 2)[0]
    pixel_array_offset = struct.unpack_from("<I", b, 10)[0]
    dib_size = struct.unpack_from("<I", b, 14)[0]
    if dib_size < 40:
        raise ValueError("Unsupported BMP DIB header size")
    width = struct.unpack_from("<i", b, 18)[0]
    height = struct.unpack_from("<i", b, 22)[0]
    planes = struct.unpack_from("<H", b, 26)[0]
    bpp = struct.unpack_from("<H", b, 28)[0]
    return {
        "file_size": file_size,
        "pixel_array_offset": pixel_array_offset,
        "width": width,
        "height": height,
        "planes": planes,
        "bpp": bpp
    }

def _row_stride(width):
    return ((width + 3) // 4) * 4

def embed_message_into_bmp(input_path, output_path, message):
    b = bytearray(read_bmp_bytes(input_path))
    header = parse_bmp_header(b)
    if header["bpp"] != 24:
        raise ValueError(f"Image is not 8-bit grayscale (bpp={header['bpp']})")
    width = header["width"]
    height = header["height"]
    pixel_offset = header["pixel_array_offset"]
    abs_height = abs(height)
    stride = _row_stride(width)
    num_pixels = width * abs_height

    message_bytes = message.encode("utf-8")
    message_length = len(message_bytes)
    total_bits = (message_length + 4) * 24
    if total_bits > num_pixels:
        raise ValueError("Message is too long to embed in the image: need {total_bits} bits, have {num_pixels} pixels (bits)")
    pixel_indices = []
    top_down = (height < 0)
    if top_down:
        row_order = range(0, abs_height)
    else:
        row_order = range(abs_height - 1, -1, -1)
    
    for row in row_order:
        row_start = pixel_offset + row * stride
        for col in range(width):
            pixel_indices.append(row_start + col)
    
    length_prefix = struct.pack("<I", message_length)
    bit_stream = []
    for byte in length_prefix + message_bytes:
        for i in range(24):
            bit_stream.append((byte >> i) & 1)

    for i, bit in enumerate(bit_stream):
        idx = pixel_indices[i]
        b[idx] = (b[idx] & 0xFE) | bit

    write_bmp_bytes(output_path, bytes(b))
    return {"output_path": output_path, "bits_writtern": len(bit_stream), "capacity_bits": num_pixels}

path = input("Enter input BMP file path: ")
if not path.lower().endswith(".bmp"):
    print("Error: Input file must have a .bmp extension.")
else:
    message = input("Enter message to embed: ")
    output_path = input("Enter output BMP file path: ")
    try:
        embed_message_into_bmp(path, output_path, message)
        print(f"Message embedded successfully into {output_path}")
    except ValueError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {path}")
