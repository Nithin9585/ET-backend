import spacy
from typing import List, Dict
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from pii_detection.models import TextSpan, DetectedEntity, EntityType
from .indian_recognizers import (
	AadhaarRecognizer,
	PANRecognizer,
	IndianPhoneRecognizer,
)

class PIIDetector:
	def __init__(self):
		try:
			# Initialize spaCy
			self.nlp = spacy.load("en_core_web_sm")
			# Initialize Presidio with custom recognizers
			self.analyzer = AnalyzerEngine()
			self.anonymizer = AnonymizerEngine()
			# Add custom Indian recognizers
			self.analyzer.registry.add_recognizer(AadhaarRecognizer())
			self.analyzer.registry.add_recognizer(PANRecognizer())
			self.analyzer.registry.add_recognizer(IndianPhoneRecognizer())
			self.is_available = True
		except (OSError, IOError, SystemExit, Exception) as e:
			self.nlp = None
			self.analyzer = None
			self.anonymizer = None
			self.is_available = False
    
	def detect_entities(self, spans: List[TextSpan], entities_to_detect: List[str]) -> List[DetectedEntity]:
		"""Detect PII entities from text spans."""
		if not self.is_available:
			return []
		
		detected_entities = []
        
		for span in spans:
			# Run Presidio analysis
			presidio_results = self.analyzer.analyze(
				text=span.text,
				entities=entities_to_detect,
				language="en"
			)
            
			# Run spaCy NER
			spacy_results = self._run_spacy_ner(span.text)
            
			# Merge results
			merged_entities = self._merge_results(
				span, presidio_results, spacy_results
			)
            
			detected_entities.extend(merged_entities)
        
		return detected_entities
    
	def _run_spacy_ner(self, text: str) -> List[Dict]:
		"""Run spaCy NER and return structured results."""
		doc = self.nlp(text)
		results = []
        
		for ent in doc.ents:
			entity_type = None
            
			# Map spaCy labels to our EntityTypes
			if ent.label_ == "PERSON":
				entity_type = "NAME"
			elif ent.label_ in ["ORG", "GPE", "LOC"]:
				entity_type = "ADDRESS"
			elif ent.label_ == "DATE":
				entity_type = "DATE_OF_BIRTH"
			elif ent.label_ in ["CARDINAL", "QUANTITY"] and self._is_medical_number(ent.text):
				entity_type = "MEDICAL_RECORD_NUMBER"
            
			if entity_type:
				results.append({
					"entity_type": entity_type,
					"start": ent.start_char,
					"end": ent.end_char,
					"score": 0.7,
					"text": ent.text
				})
        
		# Additional pattern-based detection for healthcare entities
		results.extend(self._detect_healthcare_patterns(text))
        
		return results
    
	def _merge_results(self, span: TextSpan, presidio_results, spacy_results) -> List[DetectedEntity]:
		"""Merge Presidio and spaCy results into DetectedEntity objects."""
		entities = []
        
		# Process Presidio results
		for result in presidio_results:
			mapped_type = self._map_entity_type(result.entity_type)
			if mapped_type is None:
				continue
			original_value = span.text[result.start:result.end]
			masked_value = self._mask_value(original_value, mapped_type)
			entity = DetectedEntity(
				type=EntityType(mapped_type),
				value=original_value,
				redacted_value=masked_value,
				confidence=result.score,
				method="rule",
				page_no=span.page_no,
				bbox=span.bbox,  # Use span's bbox for now
				source_span_ids=[span.span_id],
				language=span.language,
				validations={
					"regex_match": True,
					"context_score": result.score
				}
			)
			entities.append(entity)
		# Process spaCy results
		for result in spacy_results:
			mapped_type = self._map_entity_type(result["entity_type"])
			if mapped_type is None:
				continue
			original_value = result["text"]
			masked_value = self._mask_value(original_value, mapped_type)
			entity = DetectedEntity(
				type=EntityType(mapped_type),
				value=original_value,
				redacted_value=masked_value,
				confidence=result["score"],
				method="ner",
				page_no=span.page_no,
				bbox=span.bbox,
				source_span_ids=[span.span_id],
				language=span.language,
				validations={
					"spacy_label": True
				}
			)
			entities.append(entity)
		return entities

	def _map_entity_type(self, entity_type: str) -> str:
		"""Map raw entity type to supported EntityType values."""
		mapping = {
			"PERSON": "NAME",
			"ORG": "ADDRESS",
			"GPE": "ADDRESS",
			"LOC": "ADDRESS",
			"DATE": "DATE",
			"CARDINAL": "MEDICAL_RECORD_NUMBER",
			"QUANTITY": "MEDICAL_RECORD_NUMBER",
			# Add more mappings as needed
		}
		# If already a valid EntityType, return as is
		valid_types = [e.value for e in EntityType]
		if entity_type in valid_types:
			return entity_type
		return mapping.get(entity_type)
        
		return entities
    
	def _is_medical_number(self, text: str) -> bool:
		"""Check if a number pattern looks like a medical ID."""
		import re
		# Simple heuristic: alphanumeric patterns that could be medical IDs
		# More restrictive - must contain at least some digits
		cleaned_text = text.upper().replace(' ', '').replace('-', '')
        
		# Must have at least some digits to be a medical ID
		if not re.search(r'\d', cleaned_text):
			return False
            
		patterns = [
			r'^[A-Z]{2,4}[0-9]{6,12}$',  # Letters followed by numbers (MR123456789)
			r'^[0-9]{8,15}$',             # All numbers
			r'^[A-Z]{3}[0-9]{3}[A-Z]{3}[0-9]{3}$',  # Mixed pattern (ABC123DEF456)
			r'^[A-Z0-9]{6,15}$'           # General alphanumeric (but must have digits from above check)
		]
		return any(re.match(pattern, cleaned_text) for pattern in patterns) and len(cleaned_text) >= 6
    
	def _detect_healthcare_patterns(self, text: str) -> List[Dict]:
		"""Detect healthcare-specific patterns in text."""
		import re
		results = []
        
		# Medical record number patterns
		mrn_patterns = [
			r'\b(?:MRN|Medical Record|Patient ID|Chart #):\s*([A-Z0-9-]{6,15})',
			r'\b([A-Z]{2,3}\d{6,10})\b',  # Common MRN format
		]
        
		# Insurance number patterns
		insurance_patterns = [
			r'\b(?:Insurance|Policy):\s*([A-Z0-9-]{8,20})',
			r'\b([A-Z]{3}\d{6,12})\b',  # Common insurance format
		]
        
		# Medical condition keywords
		condition_keywords = [
			r'\b(?:diagnosed with|suffers from|condition:|history of)\s+([A-Za-z\s,]+?)(?:\.|,|$|\s+and|\s+or)',
			r'\b(diabetes(?:\s+mellitus)?(?:\s+type\s+\d+)?|hypertension|asthma|cancer|depression|anxiety|arthritis)\b',
		]
        
		# Medication patterns
		medication_patterns = [
			r'\b(?:prescribed|taking|medication:|drug:)\s+([A-Za-z\s]{3,30})',
			r'\b(aspirin|ibuprofen|metformin|lisinopril|atorvastatin)\b',
		]
        
		# Process all patterns
		pattern_configs = [
			(mrn_patterns, "MEDICAL_RECORD_NUMBER"),
			(insurance_patterns, "INSURANCE_NUMBER"),
			(condition_keywords, "MEDICAL_CONDITION"),
			(medication_patterns, "MEDICATION"),
		]
        
		for patterns, entity_type in pattern_configs:
			for pattern in patterns:
				for match in re.finditer(pattern, text, re.IGNORECASE):
					results.append({
						"entity_type": entity_type,
						"start": match.start(),
						"end": match.end(),
						"score": 0.8,
						"text": match.group(1) if match.groups() else match.group(0)
					})
        
		return results
    
	def _mask_value(self, value: str, entity_type: str) -> str:
		"""Mask sensitive values for storage/display."""
		if entity_type == "AADHAAR":
			return f"***-***-{value[-4:]}" if len(value) >= 4 else "***"
		elif entity_type == "PAN":
			# For PAN like ABCDE1234F, show last 2 chars of the digits (34) + last char (F)
			# So ABCDE1234F becomes *****34F
			if len(value) >= 10:  # Standard PAN format
				return f"*****{value[-3:-1]}{value[-1]}"
			elif len(value) >= 2:
				return f"*****{value[-2:]}"
			else:
				return "***"
		elif entity_type == "PHONE":
			return f"******{value[-4:]}" if len(value) >= 4 else "***"
		elif entity_type in ["MEDICAL_RECORD_NUMBER", "PATIENT_ID", "INSURANCE_NUMBER", "ACCOUNT_NUMBER"]:
			return f"***{value[-3:]}" if len(value) >= 3 else "***"
		elif entity_type == "DATE_OF_BIRTH":
			return f"**/**/****" if "/" in value else "***"
		elif entity_type in ["MEDICAL_CONDITION", "MEDICATION", "TREATMENT_INFO"]:
			# For medical info, show first word and mask rest
			words = value.split()
			if len(words) > 1:
				return f"{words[0]} ***"
			else:
				return f"{value[:2]}***" if len(value) > 2 else "***"
		else:
			# Default masking: show first 3 chars + stars for rest, but limit stars to reasonable length
			if len(value) <= 3:
				return value
			else:
				stars_count = min(len(value) - 3, 10)  # Limit to 10 stars max
				return value[:3] + "*" * stars_count
