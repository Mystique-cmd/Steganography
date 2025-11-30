# Image Steganography and Distortion Analysis

This project, `visualDistortion.py`, demonstrates Least Significant Bit (LSB) steganography for embedding secret messages into both grayscale and color images. It also provides tools to analyze the visual distortion introduced by this process using Peak Signal-to-Noise Ratio (PSNR) and Structural Similarity Index (SSIM) metrics.

## Features

*   **LSB Embedding:** Embeds random binary payloads into the least significant bit of image pixels.
*   **Grayscale Steganography:** Implements LSB embedding for single-channel (grayscale) images.
*   **Color Steganography:** Supports LSB embedding for RGB color images, either by targeting a specific channel (e.g., Red) or distributing the payload across all three channels.
*   **Visual Comparison:** Displays the original, stego (embedded), and magnified difference images for visual inspection.
*   **Quantitative Metrics:** Calculates PSNR and SSIM to objectively measure the quality degradation caused by steganography.

## Requirements

To run this program, you will need the following Python libraries:

*   `numpy`
*   `Pillow` (PIL fork)
*   `scikit-image`
*   `matplotlib`

## Installation

It's recommended to use a virtual environment to manage dependencies.

1.  **Create a virtual environment (if you haven't already):**
    ```bash
    python3 -m venv venv
    ```

2.  **Activate the virtual environment:**
    *   On Linux/macOS:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

3.  **Install the required packages:**
    ```bash
    pip install numpy Pillow scikit-image matplotlib
    ```

## Usage

1.  **Run the script:**
    ```bash
    python visualDistortion.py
    ```

2.  **Enter image paths:**
    The script will prompt you to enter the paths for a color image and a grayscale image:
    ```
    Enter color image path: image1.jpg
    Enter grayscale image path: image2.jpg
    ```
    (Replace `image1.jpg` and `image2.jpg` with your actual image file names).

3.  **View Results:**
    The script will output PSNR and SSIM values to the console and display three sets of plots sequentially:
    *   Grayscale LSB embedding
    *   Color LSB embedding (Red channel)
    *   Color LSB embedding (Distributed across RGB channels)

    You will need to close each plot window to proceed to the next set of visualizations.

## Code Structure (Key Functions)

*   `to_uint8(arr)`: Clips and converts a NumPy array to `uint8` format.
*   `embed_lsb_channel(channel, payload_bits)`: Embeds payload bits into a single image channel.
*   `random_payload(shape)`: Generates a random binary payload of a given shape.
*   `embed_grayscale_lsb(img_gray)`: Performs LSB embedding on a grayscale image.
*   `embed_color_lsb(img_rgb, mode)`: Performs LSB embedding on a color image, with `mode` being "R", "G", "B", or "distributed".
*   `compute_metrics(ref, stego, is_color)`: Calculates PSNR and SSIM between reference and stego images.
*   `visualize(ref, stego, title_prefix)`: Displays the original, stego, and difference images.
