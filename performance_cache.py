from ultralytics import YOLO
import easyocr
import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from pii_detection.indian_recognizers import AadhaarRecognizer, PANRecognizer, IndianPhoneRecognizer
import os

class ModelCache:
    yolo_model = None
    easyocr_reader = None
    spacy_nlp = None
    presidio_analyzer = None
    presidio_anonymizer = None

    @classmethod
    def load_models(cls):
        if cls.yolo_model is None:
            model_path = os.getenv("YOLO_MODEL_PATH", os.path.join(os.getcwd(), "models", "detector_yolo_1cls.pt"))
            cls.yolo_model = YOLO(model_path)
        if cls.easyocr_reader is None:
            cls.easyocr_reader = easyocr.Reader(['en'], gpu=False)
        if cls.spacy_nlp is None:
            cls.spacy_nlp = spacy.load("en_core_web_sm")
        if cls.presidio_analyzer is None:
            cls.presidio_analyzer = AnalyzerEngine()
            cls.presidio_analyzer.registry.add_recognizer(AadhaarRecognizer())
            cls.presidio_analyzer.registry.add_recognizer(PANRecognizer())
            cls.presidio_analyzer.registry.add_recognizer(IndianPhoneRecognizer())
        if cls.presidio_anonymizer is None:
            cls.presidio_anonymizer = AnonymizerEngine()

# Load models at startup
ModelCache.load_models()
