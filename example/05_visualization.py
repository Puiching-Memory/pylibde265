"""
This example demonstrates how to use the visualization module to overlay 
coding structured grids (CB, TB, PB), Intra Pred modes, and Motion Vectors on the decoded image.
"""

import pylibde265.de265 as de265
import pylibde265.visualize as visualize
import matplotlib.pyplot as plt
import os

VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"

def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: video file not found at {VIDEO_PATH}")
        return

    # Initialize decoder
    dec = de265.decoder(threads=os.cpu_count() or 1)

    print("Decoding first frame for visualization...")
    # Decode the first frame
    try:
        img = next(dec.load_file(VIDEO_PATH))
    except StopIteration:
        print("No frames decoded.")
        return

    # Get the basic image data
    y, cb, cr = img.yuv()
    
    # Use the Luma (Y) plane as the background for visualization
    vis_img = y.copy()
    
    # We need the underlying C++ image pointer for the visualize functions
    img_ptr = img.get_image_ptr()

    # Prepare subplots
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    fig.suptitle(f"libde265 Detailed Visualization - Frame {img.pts}")

    # Helper function is implicitly handled by just plotting

    # 1. Original Luma
    axes[0, 0].imshow(y, cmap='gray')
    axes[0, 0].set_title("Original (Luma)")
    axes[0, 0].axis('off')

    # 2. Coding Block (CB) Grid
    cb_grid = y.copy()
    visualize.draw_CB_grid(img_ptr, cb_grid, 255, 1)
    axes[0, 1].imshow(cb_grid, cmap='gray')
    axes[0, 1].set_title("CB Grid")
    axes[0, 1].axis('off')

    # 3. Prediction Block (PB) Grid
    pb_grid = y.copy()
    visualize.draw_PB_grid(img_ptr, pb_grid, 255, 1)
    axes[0, 2].imshow(pb_grid, cmap='gray')
    axes[0, 2].set_title("PB Grid")
    axes[0, 2].axis('off')

    # 4. Transform Block (TB) Grid
    tb_grid = y.copy()
    visualize.draw_TB_grid(img_ptr, tb_grid, 255, 1)
    axes[0, 3].imshow(tb_grid, cmap='gray')
    axes[0, 3].set_title("TB Grid")
    axes[0, 3].axis('off')

    # 5. Intra Prediction Modes
    intra_grid = y.copy()
    visualize.draw_intra_pred_modes(img_ptr, intra_grid, 255, 1)
    axes[1, 0].imshow(intra_grid, cmap='gray')
    axes[1, 0].set_title("Intra Modes")
    axes[1, 0].axis('off')

    # 6. Motion Vectors
    motion_grid = y.copy()
    visualize.draw_Motion(img_ptr, motion_grid, 1)
    axes[1, 1].imshow(motion_grid, cmap='gray')
    axes[1, 1].set_title("Motion Vectors")
    axes[1, 1].axis('off')

    # 7. Quantization (QP)
    qp_grid = y.copy()
    visualize.draw_QuantPY(img_ptr, qp_grid, 1)
    axes[1, 2].imshow(qp_grid, cmap='gray')
    axes[1, 2].set_title("Quantization (QP)")
    axes[1, 2].axis('off')

    # 8. Slices
    slice_grid = y.copy()
    visualize.draw_Slices(img_ptr, slice_grid, 1)
    axes[1, 3].imshow(slice_grid, cmap='gray')
    axes[1, 3].set_title("Slices")
    axes[1, 3].axis('off')

    plt.tight_layout()
    print("Showing plot...")
    plt.show()

if __name__ == "__main__":
    main()
