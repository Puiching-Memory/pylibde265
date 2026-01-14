import pylibde265.de265 as de265
import os

VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"

def main():
    """
    Demonstrates how to access image metadata and configure decoder parameters.
    """
    dec = de265.decoder()
    
    # --- Configuration ---
    # Set parameters before or during decoding.
    # Example: Disable deblocking filter (can improve speed if quality is less critical)
    dec.set_parameter(de265.Parameter.PARAM_DISABLE_DEBLOCKING, True)
    
    # Check if parameter was set
    is_deblocking_disabled = dec.get_parameter(de265.Parameter.PARAM_DISABLE_DEBLOCKING)
    print(f"Configuration - Deblocking Disabled: {is_deblocking_disabled}")

    # --- Metadata Access ---
    print(f"\nDecoding {VIDEO_PATH}...")
    for img in dec.load_file(VIDEO_PATH):
        print(f"--- Frame PTS: {img.pts} ---")
        
        # Dimensions
        print(f"Resolution: {img.width()}x{img.height()}")
        
        # Format Info
        print(f"Chroma Format: {img.chroma_format}")
        # Note: ChromaFormat constants: MONO=0, 420=1, 422=2, 444=3 (Check de265.pyi or docs)
        
        # Color Information
        print(f"Full Range: {bool(img.full_range)}")
        print(f"Colour Primaries: {img.colour_primaries}")
        print(f"Transfer Char: {img.transfer_characteristics}")
        print(f"Matrix Coeffs: {img.matrix_coefficients}")
        
        # NAL Header
        # nal_header() returns a dictionary with NAL unit type information
        header = img.nal_header()
        print(f"NAL Header: {header}")
        
        # Bit depth (usually 8 or 10)
        # Assuming channel 0 is Luma
        print(f"Bits per pixel: {img.get_bits_per_pixel(0)}")

if __name__ == "__main__":
    main()
