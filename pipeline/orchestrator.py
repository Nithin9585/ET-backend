

from ocr.processor import process_document
from pii_detection.detector import PIIDetector
from pii_detection.llm_validator import LLMValidator
from pii_detection.models import TextSpan, EntityType, AnalyzeResponse, DetectedEntity, BBox, Page
from ultralytics import YOLO

import os
import asyncio
from dotenv import load_dotenv

def ocr_to_textspans(ocr_result):
	pages = []
	for page in ocr_result.get("pages", []):
		spans = []
		for i, block in enumerate(page.get("blocks", [])):
			bbox = block["position"]
			span = TextSpan(
				span_id=f"span_{i}",
				text=block["text"],
				bbox=BBox(
					x1=bbox["top_left"][0],
					y1=bbox["top_left"][1],
					x2=bbox["bottom_right"][0],
					y2=bbox["bottom_right"][1]
				),
				page_no=page["page_number"],
				language="en",
				ocr_confidence=block["confidence"]
			)
			spans.append(span)
		pages.append(Page(page_no=page["page_number"], page_size={}, spans=spans))
	return pages

async def run_pipeline(image_path, llm_api_key=None):
	# Run OCR
	ocr_result = process_document(image_path)
	pages = ocr_to_textspans(ocr_result)

	# Run YOLO signature detection
	MODEL_PATH = "detector_yolo_1cls.pt"
	signature_spans = []
	try:
		model = YOLO(MODEL_PATH)
		results = model(image_path)
		unique_boxes = set()
		for i, r in enumerate(results):
			for box in r.boxes:
				x1, y1, x2, y2 = box.xyxy[0].tolist()
				conf = float(box.conf[0])
				box_key = (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2))
				if box_key in unique_boxes:
					continue
				unique_boxes.add(box_key)
				signature_span = TextSpan(
					span_id=f"signature_{i}",
					text="<signature>",
					bbox=BBox(x1=x1, y1=y1, x2=x2, y2=y2),
					page_no=1,
					language="und",
					ocr_confidence=conf
				)
				signature_spans.append(signature_span)
		# Add signature spans to first page
		if pages and signature_spans:
			pages[0].spans.extend(signature_spans)
	except Exception as e:
		print(f"Signature detection failed: {e}")

	# Entities to detect
	entities_to_detect = [e.value for e in EntityType]

	# Run PII detection
	detector = PIIDetector()
	all_spans = [span for page in pages for span in page.spans]
	pii_entities = detector.detect_entities(all_spans, entities_to_detect)

	# Optionally run LLM validation
	false_positives = []
	if llm_api_key:
		llm_validator = LLMValidator(api_key=llm_api_key)
		validated_entities, false_positives = await llm_validator.validate_entities(pii_entities, " ".join([s.text for s in all_spans]), detector)
	else:
		validated_entities = pii_entities

	# Build summary and warnings (simple example)
	summary = {"total_entities": len(validated_entities), "total_false_positives": len(false_positives)}
	warnings = []

	response = AnalyzeResponse(
		document_id=os.path.basename(image_path),
		entities=validated_entities,
		false_positives=false_positives,
		summary=summary,
		warnings=warnings
	)
	return response


if __name__ == "__main__":
	import sys
	import json
	load_dotenv()
	if len(sys.argv) < 2:
		print("Usage: python orchestrator.py <image_path> [llm_api_key]")
	else:
		image_path = sys.argv[1]
		llm_api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv("GEMINI_API_KEY")
		response = asyncio.run(run_pipeline(image_path, llm_api_key))
		print(response.json(indent=2))
