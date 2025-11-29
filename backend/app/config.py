from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017/healthease"
    mongodb_tls_insecure: bool = False  # Dev-only: allow invalid certs/hostnames
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 43200  # 30 days
    
    # API Keys
    openai_api_key: str
    razorpay_key_id: str
    razorpay_key_secret: str
    openweather_api_key: str = "demo"  # Get free key from openweathermap.org
    google_maps_api_key: str = ""  # Get from Google Cloud Console
    gemini_api_key: str = "" # Google Gemini API Key
    
    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    smtp_from: str = "noreply@healthease.com"
    
    # Application
    app_name: str = "HealthEase"
    app_version: str = "1.0.0"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Payment Configuration
    platform_fee: int = 40
    patient_referral_fee: int = 150
    hospital_share: int = 110

    # Demo auth fallback (for degraded mode without DB)
    demo_auth_enabled: bool = False
    demo_user_email: str = "demo@healthease.local"
    demo_user_password: str = "demo1234"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
