import psutil
import gc
import easyocr
import os
import tempfile
from pdf2image import convert_from_path

# Initialize EasyOCR reader cache
readers = {}

# Configurable limits
MAX_FILE_SIZE_MB = 10  # Reject files larger than 10MB
PAGE_LIMIT = 20        # Max pages to process
MAX_MEMORY_MB = 400    # Abort if memory usage exceeds 400MB

# Helper to check memory usage
def memory_ok():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    return mem_mb < MAX_MEMORY_MB

# Generator for streaming results

def process_document_stream(file_path, languages=None):
    import numpy as np
    global readers
    if not languages:
        languages = ['en']
    lang_key = tuple(languages)
    if lang_key not in readers:
        readers[lang_key] = easyocr.Reader(languages, gpu=True)
    reader = readers[lang_key]

    # File size check
    if not os.path.exists(file_path):
        yield {"error": f"File not found: {file_path}"}
        return
    if os.path.getsize(file_path) > MAX_FILE_SIZE_MB * 1024 * 1024:
        yield {"error": f"File too large (>{MAX_FILE_SIZE_MB}MB)"}
        return
    if os.path.getsize(file_path) == 0:
        yield {"error": f"File is empty: {file_path}"}
        return

    # PDF or image
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path)
        for i, pil_image in enumerate(images):
            if i >= PAGE_LIMIT:
                break
            if not memory_ok():
                yield {"error": "Memory limit exceeded"}
                return
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
                                        "top_left": np.array([bbox[0][0], bbox[0][1]], dtype=np.float16).tolist(),
                                        "top_right": np.array([bbox[1][0], bbox[1][1]], dtype=np.float16).tolist(),
                                        "bottom_right": np.array([bbox[2][0], bbox[2][1]], dtype=np.float16).tolist(),
                                        "bottom_left": np.array([bbox[3][0], bbox[3][1]], dtype=np.float16).tolist()
                                    }
                                }
                                page_data["blocks"].append(block)
                            except Exception:
                                continue
                yield page_data
                del page_results, pil_image, page_data
                gc.collect()
            except Exception:
                if os.path.exists(temp_img_path):
                    os.unlink(temp_img_path)
                gc.collect()
                yield {"error": f"EasyOCR failed for PDF page {i + 1}"}
                return
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
                    img = cv2.imread(file_path)
                    if img is None:
                        yield {"error": "Could not load image file"}
                        return
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    results = reader.readtext(img_rgb, detail=1)
                    del img, img_rgb
                    gc.collect()
                except Exception:
                    gc.collect()
                    yield {"error": "Image preprocessing failed"}
                    return
            else:
                raise img_shape_error
        except Exception:
            gc.collect()
            yield {"error": "EasyOCR readtext failed"}
            return

        if not results:
            gc.collect()
            yield {"error": "No text detected in the image."}
            return

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
                        block["position"] = {k: [np.float16(x) for x in v] for k, v in block["position"].items()}
                        page_data["blocks"].append(block)
                    except Exception:
                        continue
        yield page_data
        del results, page_data
        gc.collect()
