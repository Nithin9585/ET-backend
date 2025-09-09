import easyocr
import os
import tempfile
from pdf2image import convert_from_path

# Initialize EasyOCR reader cache
readers = {}

def process_document(file_path, languages=None):
    global readers
    if not languages:
        languages = ['en']
    lang_key = tuple(languages)
    if lang_key not in readers:
        print(f"Initializing EasyOCR reader with GPU=True for languages: {languages}")
        readers[lang_key] = easyocr.Reader(languages, gpu=True)
    reader = readers[lang_key]
    all_results = {"pages": []}

    try:
        print(f"[DEBUG] Starting OCR for file: {file_path}")
        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return {"error": f"File not found: {file_path}"}
        if os.path.getsize(file_path) == 0:
            print(f"[ERROR] File is empty: {file_path}")
            return {"error": f"File is empty: {file_path}"}
        
        print(f"[DEBUG] About to check if file is PDF: {file_path.lower().endswith('.pdf')}")

        # Check if the file is a PDF
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            for i, pil_image in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                    pil_image.save(tmp_img.name, 'PNG')
                    temp_img_path = tmp_img.name
                try:
                    page_results = reader.readtext(temp_img_path, detail=1)
                    # Log EasyOCR results for PDF page to output.txt
                    try:
                        with open("output.txt", "a", encoding="utf-8") as log_file:
                            log_file.write(f"OCR results for PDF page {i+1} of file: {file_path}\n{str(page_results)}\n\n")
                    except Exception as log_error:
                        print(f"[ERROR] Could not write OCR results to output.txt: {log_error}")
                    print(f"[DEBUG] Raw EasyOCR results for PDF page {i+1}: {page_results}")  # Debug line
                    page_data = {"page_number": i + 1, "blocks": []}
                    for detection in page_results:
                        print(f"[DEBUG] Detection: {detection}")
                        if isinstance(detection, (list, tuple)) and len(detection) >= 3:
                            bbox = detection[0]
                            text = detection[1]
                            confidence = detection[2]
                            # Validate bbox structure
                            if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                                try:
                                    block = {
                                        "text": str(text),
                                        "confidence": float(confidence),
                                        "position": {
                                            "top_left": [float(bbox[0][0]), float(bbox[0][1])],
                                            "top_right": [float(bbox[1][0]), float(bbox[1][1])],
                                            "bottom_right": [float(bbox[2][0]), float(bbox[2][1])],
                                            "bottom_left": [float(bbox[3][0]), float(bbox[3][1])]
                                        }
                                    }
                                    page_data["blocks"].append(block)
                                except (IndexError, ValueError, TypeError) as coord_error:
                                    print(f"[ERROR] Failed to process bbox coordinates: {coord_error}, bbox: {bbox}")
                                    continue
                            else:
                                print(f"[WARNING] Skipping detection with invalid bbox: {detection}")
                        else:
                            print(f"[WARNING] Skipping invalid detection: {detection}")
                    all_results["pages"].append(page_data)
                except Exception as ocr_error:
                    print(f"[ERROR] EasyOCR failed for PDF page {i + 1}: {ocr_error}")
                    return {"error": f"EasyOCR failed for PDF page {i + 1}: {ocr_error}"}
                finally:
                    if os.path.exists(temp_img_path):
                        os.unlink(temp_img_path)
        else:
            # If it's not a PDF, process it as a regular image
            print(f"[DEBUG] About to call reader.readtext() for image: {file_path}")
            try:
                # Try direct OCR first
                results = reader.readtext(file_path, detail=1)
                print(f"[DEBUG] EasyOCR call completed successfully, results type: {type(results)}")
            except ValueError as img_shape_error:
                if "too many values to unpack" in str(img_shape_error):
                    # Image format issue - try preprocessing
                    print(f"[DEBUG] Image format issue detected, preprocessing image...")
                    try:
                        import cv2
                        import numpy as np
                        # Load and convert image to proper format
                        img = cv2.imread(file_path)
                        if img is None:
                            return {"error": "Could not load image file"}
                        # Convert to RGB (EasyOCR expects RGB)
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        results = reader.readtext(img_rgb, detail=1)
                        print(f"[DEBUG] EasyOCR call with preprocessed image completed successfully")
                    except Exception as preprocess_error:
                        print(f"[ERROR] Image preprocessing failed: {preprocess_error}")
                        return {"error": f"Image preprocessing failed: {preprocess_error}"}
                else:
                    raise img_shape_error
            except Exception as ocr_error:
                print(f"[ERROR] EasyOCR readtext failed: {ocr_error}")
                import traceback
                traceback.print_exc()
                return {"error": f"EasyOCR readtext failed: {ocr_error}"}
            
            # Log EasyOCR results to output.txt
            try:
                with open("output.txt", "a", encoding="utf-8") as log_file:
                    log_file.write(f"OCR results for file: {file_path}\n{str(results)}\n\n")
            except Exception as log_error:
                print(f"[ERROR] Could not write OCR results to output.txt: {log_error}")
            print(f"[DEBUG] Raw EasyOCR results: {results}")  # Debug line

            if not results:
                print("[WARNING] No text detected in the image.")
                return {"error": "No text detected in the image."}

            page_data = {"page_number": 1, "blocks": []}
            print(f"[DEBUG] About to iterate through {len(results)} detections")
            for i, detection in enumerate(results):
                print(f"[DEBUG] Processing detection {i}: {detection}")
                if isinstance(detection, (list, tuple)) and len(detection) >= 3:
                    bbox = detection[0]
                    text = detection[1] 
                    confidence = detection[2]
                    # Validate bbox structure
                    if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                        try:
                            block = {
                                "text": str(text),
                                "confidence": float(confidence),
                                "position": {
                                    "top_left": [float(bbox[0][0]), float(bbox[0][1])],
                                    "top_right": [float(bbox[1][0]), float(bbox[1][1])],
                                    "bottom_right": [float(bbox[2][0]), float(bbox[2][1])],
                                    "bottom_left": [float(bbox[3][0]), float(bbox[3][1])]
                                }
                            }
                        except (IndexError, ValueError, TypeError) as coord_error:
                            print(f"[ERROR] Failed to process bbox coordinates: {coord_error}, bbox: {bbox}")
                            continue
                        page_data["blocks"].append(block)
                    else:
                        print(f"[WARNING] Skipping detection with invalid bbox: {detection}")
                else:
                    print(f"[WARNING] Skipping invalid detection: {detection}")
            all_results["pages"].append(page_data)

    except Exception as ocr_error:
        print(f"[ERROR] EasyOCR failed: {ocr_error}")
        return {"error": f"EasyOCR failed: {ocr_error}"}

    return all_results
