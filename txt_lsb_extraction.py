import struct 

def read_bmp_bytes(path):
    with open(path , "rb") as f:
        return f.read()

def parse_bmp_header(b):
    if len(b)< 54:
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
        "dib_size": dib_size,
        "width": width,
        "height": height,
        "planes": planes,
        "bpp": bpp,
    }

def _row_stride(width):
    return ((width + 3) // 4) * 4

def extract_message_from_bmp(input_path):
    b = bytearray(read_bmp_bytes(input_path))
    header = parse_bmp_header(b)
    if header["bpp"] != 24:
        raise ValueError(f"Image is not a 24-bit image (bpp={header['bpp']})")
    width = header["width"]
    height = header["height"]
    pixel_offset = header["pixel_array_offset"]
    abs_height = abs(height)
    stride = _row_stride(width)
    num_pixels = width * abs_height
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
        
    if num_pixels < 96:
        raise ValueError("Image is too small to contain a message")
    length_bits = [b[p] & 1 for p in pixel_indices[:96]]
    length_bytes = bytearray()
    for i in range(0, 96, 24):
        byte = 0
        for bit_index in range(24):
            byte |= (length_bits[i + bit_index] << bit_index)
        length_bytes.append(byte)
    message_len = struct.unpack("<I", length_bytes)[0]

    bits_needed = message_len * 24
    if 96 + bits_needed > num_pixels:
        raise ValueError("Image does not contain enough data for the expected message length")
    message_bits = [b[p] & 1 for p in pixel_indices[96:96 + bits_needed]]
    message_bytes = bytearray()
    for i in range(0, len(message_bits), 24):
        byte = 0
        for bit_index in range(24):
            byte |= (message_bits[i + bit_index] << bit_index)
        message_bytes.append(byte)
    return message_bytes.decode("utf-8", errors="replace")

stego_image_path = input("Enter stego BMP file path: ")
output_text_path = input("Enter output text file path: ")

hidden_message = extract_message_from_bmp(stego_image_path)
with open(output_text_path, "w") as f:
    f.write(hidden_message)
print(f"Extracted message written to {output_text_path}")
  