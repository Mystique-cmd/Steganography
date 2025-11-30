import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio,structural_similarity
import matplotlib.pyplot as plt

def to_uint8(arr):
	return np.clip(arr, 0, 255).astype(np.uint8)

def embed_lsb_channel(channel: np.ndarray, payload_bits: np.ndarray) -> np.ndarray:
	assert payload_bits.shape == channel.shape
	return (channel & 0xFE) | payload_bits

def random_payload(shape):
	return np.random.randint(0,2, size=shape, dtype=np.uint8)

def embed_grayscale_lsb(img_gray: np.ndarray) -> np.ndarray:
	payload = random_payload(img_gray.shape)
	return embed_lsb_channel(img_gray, payload)

def embed_color_lsb(img_rgb: np.ndarray, mode="distributed")->np.ndarray:
	#the distributed method embed across the 3 channels RGB
	out = img_rgb.copy()
	if mode in ( "R", "G", "B"):
		idx = {"R":0,"G":1,"B":2}[mode]
		payload = random_payload(out[..., idx].shape)
		out[..., idx] = embed_lsb_channel(out[..., idx], payload)
	elif mode == "distributed":
		for c in range (3):
			payload = random_payload(out[...,c].shape)
			out[...,c] = embed_lsb_channel(out[..., c], payload)
	else:
		raise ValueError("mode must be one of 'R','G','B','distributed")
	return out

def compute_metrics(ref: np.ndarray, stego: np.ndarray, is_color=False):
	psnr = peak_signal_noise_ratio(ref,stego, data_range=255)
	if is_color:
		ssim = structural_similarity(ref, stego, data_range=255, channel_axis=2)
	else:
		ssim = structural_similarity(ref, stego, data_range=255)
	return psnr, ssim

def visualize(ref, stego, title_prefix=""):
	diff = np.abs(ref.astype(np.int16) - stego.astype(np.int16)).astype(np.uint8)
	plt.figure(figsize=(12,4))
	plt.subplot(1,3,1); plt.imshow(ref if ref.ndim==3 else ref, cmap=None if ref.ndim==3 else "gray");plt.title(f"{title_prefix}Original");plt.axis("off")
	plt.subplot(1,3,2); plt.imshow(stego if stego.ndim==3 else stego, cmap=None if stego.ndim==3 else "gray"); plt.title(f"{title_prefix}Stego"); plt.axis("off")

	if diff.ndim == 3:
		plt.subplot(1,3,3); plt.imshow(diff*64); plt.title(f"{title_prefix}Diff x64"); plt.axis("off")
	else:
		plt.subplot(1,3,3); plt.imshow(diff * 64 , cmap="gray"); plt.title(f"{title_prefix} Diff x64"); plt.axis("off")
	plt.tight_layout()
	plt.show()

if __name__ == "__main__":
	color_path=input("Enter color image path:")
	gray_path= input("Enter grayscale image path:")

	color_img = np.array(Image.open(color_path).convert("RGB"), dtype=np.uint8)
	gray_img = np.array(Image.open(gray_path).convert("L"), dtype=np.uint8)

	gray_stego = embed_grayscale_lsb(gray_img)
	gray_psnr, gray_ssim = compute_metrics(gray_img, gray_stego, is_color=False)
	print(f"Grayscale LSB -> PSNR: {gray_psnr:.2f} dB, SSIM:{gray_ssim:.4f}")
	visualize(gray_img, gray_stego, title_prefix="Gray")

	color_stego_R = embed_color_lsb(color_img, mode="R")
	psnr_R, ssim_R = compute_metrics(color_img, color_stego_R, is_color=True)
	print(f"Color LSB (R channel) -> PSNR: {psnr_R:.2f} dB, SSIM: {ssim_R:.4f}")
	visualize(color_img, color_stego_R, title_prefix="Color R")

	color_stego_dist = embed_color_lsb(color_img, mode="distributed")
	psnr_dist, ssim_dist = compute_metrics(color_img, color_stego_dist, is_color=True)
	print(f"Color LSB (distributed) -> PSNR: {psnr_dist:.2f} dB, SSIM: {ssim_dist:.4f}")
	visualize(color_img, color_stego_dist, title_prefix="Color distributed")
