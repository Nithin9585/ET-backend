import easyocr
import os
import tempfile
from pdf2image import convert_from_path

# Initialize EasyOCR reader cache
readers = {}
from performance_cache import ModelCache

def process_document(file_path, languages=None):
    import gc
    global readers
    if not languages:
        languages = ['en']
    lang_key = tuple(languages)
    reader = ModelCache.easyocr_reader
    all_results = {"pages": []}

    # Limit number of pages/images processed (configurable)
    PAGE_LIMIT = 20  # Change as needed

    import traceback
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        if os.path.getsize(file_path) == 0:
            return {"error": f"File is empty: {file_path}"}

        # Check if the file is a PDF
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
            for i, pil_image in enumerate(images):
                if i >= PAGE_LIMIT:
                    break
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                    pil_image.save(tmp_img.name, 'PNG')
                    temp_img_path = tmp_img.name
                try:
                    page_results = reader.readtext(temp_img_path, detail=1)
                    page_data = {"page_number": i + 1, "blocks": []}
                    for detection in page_results:
                        if isinstance(detection, (list, tuple)) and len(detection) >= 3:
                            bbox = detection[0]
                            text = detection[1]
                            confidence = detection[2]
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
                                except (IndexError, ValueError, TypeError):
                                    continue
                    all_results["pages"].append(page_data)
                    del page_results, pil_image, page_data
                    gc.collect()
                except Exception as e:
                    if os.path.exists(temp_img_path):
                        os.unlink(temp_img_path)
                    gc.collect()
                    return {"error": f"EasyOCR failed for PDF page {i + 1}: {str(e)}\n{traceback.format_exc()}"}
                finally:
                    if os.path.exists(temp_img_path):
                        os.unlink(temp_img_path)
                    gc.collect()
        else:
            try:
                results = reader.readtext(file_path, detail=1)
            except ValueError as img_shape_error:
                if "too many values to unpack" in str(img_shape_error):
                    try:
                        import cv2
                        import numpy as np
                        img = cv2.imread(file_path)
                        if img is None:
                            return {"error": "Could not load image file"}
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        results = reader.readtext(img_rgb, detail=1)
                        del img, img_rgb
                        gc.collect()
                    except Exception as e:
                        gc.collect()
                        return {"error": f"Image preprocessing failed: {str(e)}\n{traceback.format_exc()}"}
                else:
                    raise img_shape_error
            except Exception as e:
                gc.collect()
                return {"error": f"EasyOCR readtext failed: {str(e)}\n{traceback.format_exc()}"}

            if not results:
                gc.collect()
                return {"error": "No text detected in the image."}

            page_data = {"page_number": 1, "blocks": []}
            for detection in results:
                if isinstance(detection, (list, tuple)) and len(detection) >= 3:
                    bbox = detection[0]
                    text = detection[1]
                    confidence = detection[2]
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
                        except (IndexError, ValueError, TypeError):
                            continue
                        page_data["blocks"].append(block)
            all_results["pages"].append(page_data)
            del results, page_data
            gc.collect()

    except Exception as e:
        gc.collect()
        return {"error": f"EasyOCR failed: {str(e)}\n{traceback.format_exc()}"}

    gc.collect()
    return all_results
