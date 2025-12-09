"""struct is a standard module used to convert between python values and  C- binary data..
It lets you pack values into bytes and unpack bytes back into values, which is essential for working
with  binary files, network protocols or interfacing with C libraries"""
import struct

""" The function 'read_bmp_bytes' takes the path to the file as a parameter.  Opens the file in the
path using with to ensure it is closed automatically. The file is opened in read mode binary format ( rb )"""
def read_bmp_bytes(path):
    with open(path , "rb") as f:
        return f.read()

"""The function 'write_bmp_bytes' takes the path and data as arguments. The data argument represents the
complete binary content of the BMP image that will be written to a file. Data = raw binary data of original image +
the secret message now embedded inside it. The wb format is write mode and binary mode"""
def write_bmp_bytes(path, data):
    with open (path, "wb") as f:
        f.write(data)

"""the b argument is a bytearray that contains the entire binary content of the BMP image file.write_bmp_bytes
 b=bytearray(read_bmp_bytes(path). A bytearray is a built-in data type that represents a  sequence of  bytes.Its most
 important characteristic is that it is mutable ( its content can be changed after its created) This is what makes it different
 from the byte object.For this particular file, the program needs to alter the individual bytes of the image to hide the message.read_bmp_bytes
 1. It reads the image into a byte array
 2. It directly modifies the values within that bytearray to embed message one bit at a time
 The number 54 is used to compare the bytearray length because it is the size of the combined headers for a standard windows BMP file.read_bmp_bytes
 A BMP file header is typically split into two:
 1. File header ( 14 Bytes) : this is the part that identifies the file as a BMP, contains the total file size , and specifies the offset where the actual image
  pixel data begins
  2. DIB Header(40 bytes): This is the device independent bitmap header( specifically the common BITMAPINFOHEADER version ) which contains essential
  metadata about the image, such as width, height and bits per pixel"""
def parse_bmp_header(b):
    if len(b) < 54:
        raise ValueError("Not a valid BMP(too small)")

""" This if statement is checking for the file signature( aka the magic number). b[0:2] slices the bytearray to get the first two bytes of the file
b 'BM' represents the characters B and M as bytes. Almost all BMP files are required to start with this two characters and that is why they act as the file signature"""
    if b[0:2] != b 'BM':
        raise ValueError("Not a BMP file (missing BM header)")

""" The [0] at the end of the lines are there because of how the struct.unpack_from function works. struct.unpack_from() always returns the result in a tuple. This is because
you can ask it to unpack multiple values at once( e.g struct.unpack_from ('II',...) to get two integers. In this case the code asks for one value '<I' which mean one unsigned
integer. A BMP file has two main parts:
1. Header section ( at the beginning ) : contains the metadata,( width, height, colors), file_size,dib_size and pixel_array_offset
2. Pixel data section( the rest of the file) : this is the main part containing th actual color data for every single pixel that makes up the image. The pixel_array_offset is a crucial
no. stored in the header. It tells you the exact number of bytes you must skip from the beginning of the file to find where the actual image content begins. While the header is
54 bytes it is not guaranteed. The pixel array offset value provides the correct starting point
Each struct.unpack_from() call is precisely targeted to read a specific piece of metadata from the files bytearray. This is the signature of th function struct.unpack_from(format,
buffer, offset)
1. Format( i.e  '<I','<II', '<H' ) This is a string that tells the function what to read. The first character < specifies the byte order. It stands for little-endian which is the
standard byte order for BMP files. It means that for a multi bytes number the LSB is stored first. The second char specifies the data type II is for signed integers. It is used
for image width and height, as negative height has a special meaning( it indicates a top down image). Its 4 bytes. H on the other hand  ( 2 bytes ) represents an unsigned short
used for smaller values like bits per pixes ( bpp)
2. Buffer ( b) : this is the source of the data - the complete byte array of the image file
3. Offset : this is the exact byte position in the file where where the data for that specific field begins. These numbers are not random; they are defined by the BMP file
format specification"""
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

"""In BMP file format, each row of pixel data is required to be padded with extra bytes so that its total length is a multiple of 4. This is done for performance reasons
related to memory alignment. The total length of one row in bytes ( pixels + padding) is called stride. The common integer arithmetic trick used to round up a number to the
nearest multiple of 4 is the one used below. The integer division // 4 divides by 4 and discards the remainder"""
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
    stride = _row_stride(width * 3)
    num_pixels = width * abs_height

    message_bytes = message.encode("utf-8")
    message_length = len(message_bytes)

    """It adds 4 bytes of to the message length because the script plans  to hide the length of the message( as a 4 byte integer ) in the image first. This is so that the
    extraction tool knows how many bytes to read.
    A positive height means that the image is stored bottom-up . For a 24 bit image each pixel is 3 bytes ( BLue Green Red)"""
    total_bits = (message_length + 4) * 8
    if total_bits > num_pixels:
        raise ValueError("Message is too long to embed in the image: need {total_bits} bits, have {num_pixels} pixels (bits)")
    pixel_indices = []
    top_down = (height < 0)
    if top_down:
        row_order = range(0, abs_height)
    else:
    """ This line is creating a sequence of numbers to process the image rows in reverse order. This is necessary for standard  bottom up BMP files where the pixel data for
    the last row of the image is stored first in the file. The function is like range ( start, stop, step)
    1. start = abs_height -1 : this is the first parameter. If an image is for instance 100 pixels high, its rows are indexed from 0 - 99 , abs_height - 1 gives you the index of
    the very last row  99. This is where the loop will start
    2. stop = -1 : this parameter is the value the sequence goes up to but does not include . Since the loop is counting down to include row 0 , setting the stop value to -1
     ensures that 0 is the last number generated before the sequence stops
     3. step = -1 : this parameter is the amount of change by each time. A step of -1 means the function will cound backwards one by one"""
        row_order = range(abs_height - 1, -1, -1)
    
    for row in row_order:
        row_start = pixel_offset + row * stride
        for col in range(width):
            pixel_indices.append(row_start + col * 3)
    
    length_prefix = struct.pack("<I", message_length)
    bit_stream = []
    for byte in length_prefix + message_bytes:
        for i in range(8):

""" imagine our byte is the char H which means its the value of 72. In an 8 bit binary this is 01001000. The loop variable i will go from 0 -7 to get each of the 8 bits
1. >> ( The right shift operator ) byte >> i shifts all the bits in the byte to the right by i positions. The bits tha fall off the  right are discarded. Lets say i = 3 . We want to get
the 4th bit from the right original = 001001000 shifter by 3 = 00001001
 The bitwise AND operator compares the bits of two numbers"""
            bit_stream.append((byte >> i) & 1)

    for i, bit in enumerate(bit_stream):
        idx = pixel_indices[i]

""" This is where a single bit of the secret message is hidden inside a single byte of the image file. This technique is called the LSB Steganography. The LSB is the
rightmost bit in a byte. Changing it has the smallest possible impact on the byte's total value, making the modification difficult to detect visually.
1. (b[idx] & 00xFE) - clearing the last bit. 00xFE is a decimal number 254
2. (...)|bit - sets the new bit"""
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
