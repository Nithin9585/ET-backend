from pydantic import BaseModel, Field
from typing import List, Dict, Any
from enum import Enum

class EntityType(str, Enum):
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    NAME = "NAME"
    ADDRESS = "ADDRESS"
    AGE = "AGE"
    SEX = "SEX"
    GENDER = "GENDER"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    MEDICAL_RECORD_NUMBER = "MEDICAL_RECORD_NUMBER"
    PATIENT_ID = "PATIENT_ID"
    INSURANCE_NUMBER = "INSURANCE_NUMBER"
    ACCOUNT_NUMBER = "ACCOUNT_NUMBER"
    MEDICAL_CONDITION = "MEDICAL_CONDITION"
    MEDICATION = "MEDICATION"
    TREATMENT_INFO = "TREATMENT_INFO"
    SIGNATURE = "SIGNATURE"

class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class TextSpan(BaseModel):
    span_id: str
    text: str
    bbox: BBox
    page_no: int
    language: str = "en"
    ocr_confidence: float = 1.0

class Page(BaseModel):
    page_no: int
    page_size: Dict[str, Any]
    spans: List[TextSpan]

class AnalyzeRequest(BaseModel):
    document_id: str
    file_type: str = "pdf"
    pages: List[Page]
    options: Dict[str, Any] = Field(default_factory=lambda: {
        "entities_to_detect": [
            "AADHAAR", "PAN", "PHONE", "EMAIL", "NAME", "ADDRESS", "AGE", "SEX", "GENDER", "DATE_OF_BIRTH",
            "MEDICAL_RECORD_NUMBER", "PATIENT_ID", "INSURANCE_NUMBER", "ACCOUNT_NUMBER",
            "MEDICAL_CONDITION", "MEDICATION", "TREATMENT_INFO"
        ],
        "use_llm_validation": False,
        "languages": ["en", "hi"],
    })

class DetectedEntity(BaseModel):
    type: EntityType
    value: str
    redacted_value: str
    confidence: float
    method: str
    page_no: int
    bbox: BBox
    source_span_ids: List[str]
    language: str
    validations: Dict[str, Any] = Field(default_factory=dict)

class AnalyzeResponse(BaseModel):
    document_id: str
    entities: List[DetectedEntity]
    false_positives: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Dict[str, Any]
    warnings: List[str] = Field(default_factory=list)
