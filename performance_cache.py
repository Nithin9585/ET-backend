import os
from ultralytics import YOLO
import easyocr
import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from pii_detection.indian_recognizers import AadhaarRecognizer, PANRecognizer, IndianPhoneRecognizer

class ModelCache:
    yolo_model = None
    easyocr_reader = None
    spacy_nlp = None
    presidio_analyzer = None
    presidio_anonymizer = None

    @classmethod
    def load_yolo(cls):
        env_path = os.getenv("YOLO_MODEL_PATH")
        local_path = os.path.join(os.getcwd(), "detector_yolo_1cls.pt")
        if env_path and os.path.exists(env_path):
            model_path = env_path
        elif os.path.exists(local_path):
            model_path = local_path
        else:
            raise FileNotFoundError(f"YOLO model file not found at {env_path} or {local_path}")
        cls.yolo_model = YOLO(model_path)

    @classmethod
    def load_easyocr(cls):
        if cls.easyocr_reader is None:
            cls.easyocr_reader = easyocr.Reader(['en'], gpu=False)

    @classmethod
    def load_spacy(cls):
        if cls.spacy_nlp is None:
            cls.spacy_nlp = spacy.load("en_core_web_sm")

    @classmethod
    def load_presidio(cls):
        if cls.presidio_analyzer is None:
            cls.presidio_analyzer = AnalyzerEngine()
            cls.presidio_analyzer.registry.add_recognizer(AadhaarRecognizer())
            cls.presidio_analyzer.registry.add_recognizer(PANRecognizer())
            cls.presidio_analyzer.registry.add_recognizer(IndianPhoneRecognizer())
        if cls.presidio_anonymizer is None:
            cls.presidio_anonymizer = AnonymizerEngine()