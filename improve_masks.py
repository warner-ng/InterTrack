#!/usr/bin/env python3
"""
Mask generation utility for custom video data
使用 OpenCV 边界框和颜色阈值生成人物和物体掩码
"""
import os
import cv2
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def get_improved_person_mask(rgb_frame):
    """
    Improved person mask using edge detection and morphology
    """
    # Convert to grayscale
    gray = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    # Use Canny edge detection
    edges = cv2.Canny(gray, 100, 200)
    
    # Dilate edges to form closed contours
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    dilated = cv2.dilate(edges, kernel, iterations=3)
    
    # Fill large regions
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    h, w = gray.shape
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Find and draw large contours
    areas = [cv2.contourArea(c) for c in contours]
    if areas:
        mean_area = np.mean(areas)
        for i, cnt in enumerate(contours):
            # Draw contours that are reasonably sized
            if areas[i] > mean_area * 0.05:
                cv2.drawContours(mask, [cnt], 0, 255, -1)
    
    # If still too uniform, use a different approach
    if np.mean(mask) > 200 or np.mean(mask) < 50:
        # Fallback to threshold-based segmentation
        _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    return mask

def get_improved_object_mask(rgb_frame, person_mask):
    """
    Improved object detection by looking for high-contrast dark regions
    """
    h, w = rgb_frame.shape[:2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to preserve edges
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Use multiple thresholds to find dark regions
    # Try different ranges for dark objects
    dark_mask1 = cv2.inRange(filtered, 0, 100)
    dark_mask2 = cv2.inRange(filtered, 100, 150)
    
    # Combine masks
    obj_mask = cv2.bitwise_or(dark_mask1, dark_mask2)
    
    # Remove very small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    obj_mask = cv2.morphologyEx(obj_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Subtract person region
    if person_mask is not None:
        person_inv = cv2.bitwise_not(person_mask)
        obj_mask = cv2.bitwise_and(obj_mask, person_inv)
    
    # Keep only large connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(obj_mask)
    large_mask = np.zeros_like(obj_mask)
    
    min_area = max(h * w * 0.002, 300)  # At least 0.2% or 300 pixels
    
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] > min_area:
            large_mask[labels == i] = 255
    
    return large_mask if np.sum(large_mask) > 0 else obj_mask

def process_frames_improved(frames_dir):
    """
    Process all frames with improved methods
    """
    frames_dir = Path(frames_dir)
    frame_files = sorted(frames_dir.glob('frame_*.color.jpg'))
    
    print(f"Found {len(frame_files)} frames to process with improved method")
    
    for idx, frame_file in enumerate(frame_files):
        if (idx + 1) % 10 == 0:
            print(f"Processing frame {idx + 1}/{len(frame_files)}")
        
        rgb_frame = cv2.imread(str(frame_file))
        if rgb_frame is None:
            print(f"Failed to read {frame_file}")
            continue
        
        # Get improved masks
        person_mask = get_improved_person_mask(rgb_frame)
        object_mask = get_improved_object_mask(rgb_frame, person_mask)
        
        # Save masks, overwriting old ones
        base_name = frame_file.stem.replace(".color", "")
        person_mask_path = frames_dir / f"{base_name}.person_mask.png"
        object_mask_path = frames_dir / f"{base_name}.obj_rend_mask.png"
        
        cv2.imwrite(str(person_mask_path), person_mask)
        cv2.imwrite(str(object_mask_path), object_mask)
    
    print(f"✓ Regenerated masks for {len(frame_files)} frames with improved method")
    return len(frame_files)

if __name__ == "__main__":
    frames_dir = "/home/warner/_projects/InterTrack/demo-data/carrying_bike/frames"
    print("Regenerating masks with improved segmentation methods...\n")
    process_frames_improved(frames_dir)
    
    # Verify
    mask_files = list(Path(frames_dir).glob("*.person_mask.png"))
    print(f"\n✓ Person masks: {len(mask_files)}")
    obj_files = list(Path(frames_dir).glob("*.obj_rend_mask.png"))
    print(f"✓ Object masks: {len(obj_files)}")
