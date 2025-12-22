import struct

def bytes_to_bits (data: bytes):
	bits = []
	for byte in data:
		for i in range( 7, -1, -1 ):
			bits .append((byte >> i) & 1)
		return bits
		
def bits_to_bytes(bits):
	if len(bits) % 8 != 0:
		bits = bits + [0] * (8 -(len(bits) % 8))
	result = bytearray()
	for i in range ( 0 , len(bits), 8):
		byte = 0
	for b in bits[i:i+8]:
		byte = (byte << 1) | b
	result.append(byte)
	return bytes(result)
	
def embed_2bit_lsb_bmp(cover_bm_path, stego_bmp_path, payload: bytes):
	with open (cover_bmp_path, "rb") as f:
		bmp_data = bytearray(f.read())
		pixel_data_offset = struct.unpack_from("<I", bmp_data, 10)[0]
		width = struct.unpack_from("<I", bmp_data, 18)[0]
		height = struct.unpack_from("<I", bmp_data, 22)[0]
		bpp = struct.unpack_from("<H", bmp_data, 28)[0]
		if bpp != 24:
			raise ValueError ("This function only supports 24-bit BMP images")
			
		row_size = (width * 3 + 3) & ~3
		pixel_array_size = row_size * height
		
		payload_len = len(payload)
		header = struct.pack("<I", payload_len)
		full_payload = header + payload
		
		payload_bits = bytes_to_bits(full_payload)
		total_payload_bits = len(payload_bits)
		
		num_pixels = width * height
		capacity_bits = num_pixels * 6
		
		if total_payload_bits > capacity_bits:
			raise ValueError (f"Payload too large: Capacity: {capacity_bits}, need: {total_payload_bits} bits.")
			
		bit_index = 0
		for row in range(height):
			row_start = pixel_data_offset + row * row_size
			for col in range(width):
				pixel_index = row_start + col * 3
				
				for channel_offset in range(3):
					if bit_index >= total_payload_bits:
						break
						
					bit0 = payload_bits[bit_index] if bit_index < total_payload_bits else 0
					bit1 = payload_bits[bit_index + 1] if bit_index +1 < total_payload_bits else 0
					bit_index +=2
					
					two_bits  = (bit0 << 1) | bit1
					channel_value = bmp_data[pixel_index + channel_offset]
					
					channel_value = (channel_value & 0b11111100)| two_bits
					bmp_data[pixel_index + channel_offset] = channel_value
					
				if bit_index >= total_payload_bits:
					break
			if bit_index >= total_payload_bits:
				break
				
		with open (stego_bmp_path, "wb") as f:
			f.write(bmp_data)
	
if __name__ == "__main__":
	cover_bmp_path = input( "Path to the BMP file :")
	stego_bmp_path = input("Output path:")
	
	secret_message = input( "What is your message?")
	payload_bytes = secret_message.encode("utf-8")
	
	embed_2bit_lsb_bmp(cover_bmp_path, stego_bmp_path, payload_bytes)
	print("[ + ] Embedding message ...")
	print("[ ! ] Embedding done.")
	
	
