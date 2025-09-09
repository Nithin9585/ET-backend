from presidio_analyzer import Pattern, PatternRecognizer

class AadhaarRecognizer(PatternRecognizer):
    PATTERNS = [
        Pattern("Aadhaar (strong)", r"\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b", 0.9),
        Pattern("Aadhaar (medium)", r"\b(?![01]|0000|1111|2222|3333|4444|5555|6666|7777|8888|9999)\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", 0.7),
    ]
    CONTEXT = ["aadhaar", "adhar", "aadhaar card", "uid", "unique", "identification"]
    def __init__(self):
        super().__init__(supported_entity="AADHAAR", patterns=self.PATTERNS, context=self.CONTEXT, supported_language="en")

class PANRecognizer(PatternRecognizer):
    PATTERNS = [
        Pattern("PAN (strong)", r"\b[A-Z]{5}\d{4}[A-Z]\b", 0.9),
    ]
    CONTEXT = ["pan", "permanent account number", "tax", "income tax", "financial", "account"]
    def __init__(self):
        super().__init__(supported_entity="PAN", patterns=self.PATTERNS, context=self.CONTEXT, supported_language="en")

class IndianPhoneRecognizer(PatternRecognizer):
    PATTERNS = [
        Pattern("Phone (strong international)", r"\+91[-\s]?[6-9]\d{9}\b", 0.9),
        Pattern("Phone (strong mobile)", r"\b[6-9]\d{9}\b", 0.8),
        Pattern("Phone (landline with area code)", r"\b0\d{2,4}[-\s]?\d{6,8}\b", 0.7),
    ]
    CONTEXT = ["phone", "mobile", "contact", "number"]
    def __init__(self):
        super().__init__(supported_entity="PHONE", patterns=self.PATTERNS, context=self.CONTEXT, supported_language="en")
