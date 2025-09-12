from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from performance_cache import ModelCache
import tempfile
import os
import logging
from performance_cache import ModelCache
from ocr.processor import process_document
from pii_detection.detector import PIIDetector
from pii_detection.models import TextSpan, EntityType, DetectedEntity
from pii_detection.llm_validator import LLMValidator
from dotenv import load_dotenv
import shutil
from config.settings import settings
from config.logging import logger

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="OCR PII Detection API",
    description="Production-ready OCR and PII detection service",
    version="1.0.0",
    debug=settings.debug
)

from fastapi.middleware.cors import CORSMiddleware
# Add CORS middleware for all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)



@app.on_event("startup")
async def startup_event():
    ModelCache.load_yolo()
    ModelCache.load_easyocr()
    ModelCache.load_spacy()
    ModelCache.load_presidio()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "OCR PII Detection API",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "OCR PII Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process_document": "/process_document",
            "docs": "/docs"
        }
    }

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
    allowed_extensions = settings.get_allowed_extensions_set()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_ext}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )


@app.post("/process_document")
async def process_document_api(
    file: UploadFile = File(...),
    use_llm: bool = Form(False)
):
    """Process document for OCR, signature detection, and PII detection."""
    
    # Validate input file
    validate_file(file)
    
    logger.info(f"Processing document: {file.filename}")
    
    llm_api_key = settings.gemini_api_key if use_llm else None
    image_path = None

    try:
        # Save uploaded file to temp file
        orig_ext = os.path.splitext(file.filename)[1] or '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=orig_ext) as tmp:
            file_bytes = await file.read()
            tmp.write(file_bytes)
            image_path = tmp.name

        print(f"[DEBUG] Temp file created at: {image_path}, size: {os.path.getsize(image_path)} bytes, ext: {orig_ext}")

        # Ensure file is valid
        if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
            print(f"[ERROR] Temp file not found or empty: {image_path}")
            raise HTTPException(status_code=400, detail="Uploaded file could not be saved.")

        # Run OCR
        ocr_result = process_document(image_path)
        if ocr_result is None or (isinstance(ocr_result, dict) and "error" in ocr_result):
            error_msg = ocr_result["error"] if ocr_result and "error" in ocr_result else "OCR failed"
            return JSONResponse(content={"error": error_msg}, status_code=400)

        # Run YOLO signature detection
        signature_spans = []
        try:
            model = ModelCache.yolo_model
            results = model(image_path)
            unique_boxes = set()
            detected_boxes = 0
            for i, r in enumerate(results):
                for box in r.boxes:
                    coords = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    if len(coords) >= 4:
                        x1, y1, x2, y2 = coords[:4]
                    else:
                        print(f"[SIGNATURE] Skipping YOLO box with insufficient coordinates: {coords}")
                        continue
                    box_key = (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2))
                    if box_key in unique_boxes:
                        continue
                    unique_boxes.add(box_key)
                    signature_spans.append({
                        "span_id": f"signature_{i}",
                        "text": "<signature>",
                        "bbox": {
                            "x1": float(x1),
                            "y1": float(y1),
                            "x2": float(x2),
                            "y2": float(y2)
                        },
                        "page_no": 1,
                        "language": "und",
                        "ocr_confidence": conf
                    })
                    detected_boxes += 1
                    print(f"[SIGNATURE] Detected box {detected_boxes}: coords={coords}, confidence={conf}")
            print(f"[SIGNATURE] Total detected signature boxes: {detected_boxes}")
        except Exception as e:
            print(f"[SIGNATURE][ERROR] Signature detection failed: {e}")
            signature_spans = []

        # Build spans for PII detection
        spans_for_pii = []
        for page in ocr_result.get("pages", []):
            for i, block in enumerate(page.get("blocks", [])):
                span = TextSpan(
                    span_id=f"block_{i}",
                    text=block["text"],
                    bbox={
                        "x1": block["position"]["top_left"][0],
                        "y1": block["position"]["top_left"][1],
                        "x2": block["position"]["bottom_right"][0],
                        "y2": block["position"]["bottom_right"][1]
                    },
                    page_no=page["page_number"],
                    language="en",
                    ocr_confidence=block["confidence"]
                )
                spans_for_pii.append(span)

            # Add signature spans to first page
            if page["page_number"] == 1 and signature_spans:
                for sig in signature_spans:
                    sig_span = TextSpan(
                        span_id=sig["span_id"],
                        text=sig["text"],
                        bbox=sig["bbox"],
                        page_no=sig["page_no"],
                        language=sig["language"],
                        ocr_confidence=sig["ocr_confidence"]
                    )
                    spans_for_pii.append(sig_span)

        # Entities to detect
        entities_to_detect = [e.value for e in EntityType]

        # Run PII detection
        try:
            detector = PIIDetector()
            pii_entities = detector.detect_entities(spans_for_pii, entities_to_detect)
        except Exception as pii_error:
            print(f"[WARNING] PII detection failed: {pii_error}")
            pii_entities = []

        # Optionally run LLM validation
        false_positives = []
        import logging
        if llm_api_key:
            try:
                llm_validator = LLMValidator(api_key=llm_api_key)
                validated_entities, false_positives = await llm_validator.validate_entities(
                    pii_entities, " ".join([s.text for s in spans_for_pii]), detector
                )
            except Exception as llm_error:
                logging.error(f"LLM validation failed: {llm_error}")
                validated_entities = pii_entities
        else:
            logging.warning("LLM validation skipped: GEMINI_API_KEY not set.")
            validated_entities = pii_entities

        # Convert DetectedEntity objects to dicts for JSON response
        pii_data = [e.dict() for e in validated_entities]

        return JSONResponse(content={
            "ocr": ocr_result,
            "signatures": signature_spans,
            "pii_detection": pii_data,
            "false_positives": false_positives
        })

    except Exception as e:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Ensure temp file is always cleaned up
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
