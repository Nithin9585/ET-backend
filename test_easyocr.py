#!/usr/bin/env python3
"""
Simple EasyOCR test script to debug the unpacking error
"""
import easyocr
import sys
import traceback

def test_easyocr(image_path):
    print(f"Testing EasyOCR with image: {image_path}")
    
    try:
        # Initialize reader
        print("Initializing EasyOCR reader...")
        reader = easyocr.Reader(['en'], gpu=False)  # Use CPU to avoid GPU issues
        print("EasyOCR reader initialized successfully")
        
        # Try OCR
        print("Calling reader.readtext()...")
        results = reader.readtext(image_path, detail=1)
        print(f"OCR completed successfully!")
        print(f"Results type: {type(results)}")
        print(f"Number of results: {len(results) if results else 0}")
        
        if results:
            print("First few results:")
            for i, result in enumerate(results[:3]):
                print(f"  Result {i}: {result}")
                print(f"    Type: {type(result)}")
                print(f"    Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        
        return results
        
    except Exception as e:
        print(f"ERROR in EasyOCR: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test with the problematic image
    image_path = r"C:\Users\Nithi\OneDrive\Pictures\Camera Roll\WhatsApp Image 2025-09-03 at 02.16.44_9242bb28.jpg"
    results = test_easyocr(image_path)
