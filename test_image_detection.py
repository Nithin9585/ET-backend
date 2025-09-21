#!/usr/bin/env python3
"""
Test script for image detection functionality in OCR processor
"""
import os
import sys
from ocr.processor import process_document

def test_image_detection():
    """Test the image detection functionality."""
    
    # Test with a sample image file (you can provide your own image path)
    test_image_path = "test_image.jpg"  # Replace with actual test image
    
    if not os.path.exists(test_image_path):
        print("❌ Test image not found. Please provide a test image file.")
        print("Usage: Place a test image file named 'test_image.jpg' in the backend-app directory")
        return False
    
    try:
        print(f"🔍 Testing image detection on: {test_image_path}")
        
        # Test with image detection enabled
        result_with_images = process_document(test_image_path, detect_images=True)
        
        # Test with image detection disabled
        result_without_images = process_document(test_image_path, detect_images=False)
        
        print("\n📄 OCR Results:")
        print(f"  - Pages processed: {len(result_with_images.get('pages', []))}")
        
        print("\n🖼️ Image Detection Results:")
        detected_images = result_with_images.get('detected_images', [])
        if detected_images:
            print(f"  - Images detected on {len(detected_images)} page(s)")
            for page_data in detected_images:
                page_num = page_data['page_number']
                images = page_data['images']
                print(f"    📄 Page {page_num}: {len(images)} image(s) detected")
                for i, img in enumerate(images):
                    print(f"      🖼️ Image {i+1}: {img['type']} (confidence: {img['confidence']:.2f})")
        else:
            print("  - No images detected")
        
        print("\n✅ Image detection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during image detection test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_image_detection()
    sys.exit(0 if success else 1)