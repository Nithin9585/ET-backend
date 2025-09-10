"""
Production Configuration Management
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Server Configuration
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=int(os.environ.get("PORT", "8000")), env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # API Configuration
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(default=["jpg", "jpeg", "png", "pdf"], env="ALLOWED_EXTENSIONS")
    request_timeout: int = Field(default=60, env="REQUEST_TIMEOUT")
    
    # OCR Configuration
    ocr_gpu_enabled: bool = Field(default=True, env="OCR_GPU_ENABLED")
    ocr_languages: List[str] = Field(default=["en"], env="OCR_LANGUAGES")
    ocr_confidence_threshold: float = Field(default=0.5, env="OCR_CONFIDENCE_THRESHOLD")
    
    # YOLO Configuration
    yolo_model_path: str = Field(default="models/detector_yolo_1cls.pt", env="YOLO_MODEL_PATH")
    yolo_confidence_threshold: float = Field(default=0.5, env="YOLO_CONFIDENCE_THRESHOLD")
    
    # PII Detection Configuration
    pii_detection_enabled: bool = Field(default=True, env="PII_DETECTION_ENABLED")
    spacy_model: str = Field(default="en_core_web_sm", env="SPACY_MODEL")
    
    # LLM Validation Configuration
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    llm_validation_enabled: bool = Field(default=True, env="LLM_VALIDATION_ENABLED")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    enable_file_logging: bool = Field(default=True, env="ENABLE_FILE_LOGGING")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def get_allowed_extensions_set(self) -> set:
        """Get allowed extensions as a set for faster lookup."""
        if isinstance(self.allowed_extensions, str):
            return set(ext.strip().lower() for ext in self.allowed_extensions.split(","))
        return set(ext.lower() for ext in self.allowed_extensions)


# Global settings instance
settings = Settings()
