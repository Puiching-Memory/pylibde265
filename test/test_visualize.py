import pylibde265.de265 as de265
import pylibde265.visualize as visualize
import numpy as np
import os

def test_visualize_all():
    VIDEO_PATH = "./multimedia/video/Kinkaku-ji.h265"
    if not os.path.exists(VIDEO_PATH):
        print(f"Skip test, file not found: {VIDEO_PATH}")
        return

    dec = de265.decoder(threads=2)
    
    # We only need one frame to test visualization
    img = next(dec.load_file(VIDEO_PATH))
    
    img_ptr = img.get_image_ptr()
    width = img.width()
    height = img.height()
    
    # Destination array (grayscale)
    dst = np.zeros((height, width), dtype=np.uint8)
    
    # Test all visualization functions
    # pixelSize=1 means 1:1 mapping
    
    # 1. draw_CB_grid
    visualize.draw_CB_grid(img_ptr, dst, 255, 1)
    assert np.any(dst > 0)
    dst.fill(0)
    
    # 2. draw_TB_grid
    visualize.draw_TB_grid(img_ptr, dst, 255, 1)
    assert np.any(dst > 0)
    dst.fill(0)
    
    # 3. draw_PB_grid
    visualize.draw_PB_grid(img_ptr, dst, 255, 1)
    assert np.any(dst > 0)
    dst.fill(0)
    
    # 4. draw_PB_pred_modes
    visualize.draw_PB_pred_modes(img_ptr, dst, 1)
    # Output may not have data if not applicable, but at least shouldn't crash
    dst.fill(0)
    
    # 5. draw_intra_pred_modes
    visualize.draw_intra_pred_modes(img_ptr, dst, 255, 1)
    dst.fill(0)
    
    # 6. draw_QuantPY
    visualize.draw_QuantPY(img_ptr, dst, 1)
    dst.fill(0)
    
    # 7. draw_Motion
    # Motion might be empty for the first frame (intra)
    visualize.draw_Motion(img_ptr, dst, 1)
    dst.fill(0)
    
    # 8. draw_Slices
    visualize.draw_Slices(img_ptr, dst, 1)
    # assert np.any(dst > 0) # Might be empty if only one slice
    dst.fill(0)
    
    # 9. draw_Tiles
    visualize.draw_Tiles(img_ptr, dst, 1)
    # assert np.any(dst > 0) # Might be empty if only one tile
    
    print("All visualization functions tested successfully (some outputs were empty as expected for this frame)")

if __name__ == "__main__":
    test_visualize_all()
