import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # API Keys
        openai_api_key: str
            hubspot_api_key: str
                supabase_url: str
                    supabase_key: str
                        google_client_id: str
                            google_client_secret: str
                                google_refresh_token: str
                                    
                                        # Database
                                            database_url: str = "sqlite:///./email_automation.db"
                                                
                                                    # Security
                                                        secret_key: str
                                                            algorithm: str = "HS256"
                                                                access_token_expire_minutes: int = 30
                                                                    
                                                                        # Monitoring
                                                                            enable_metrics: bool = True
                                                                                log_level: str = "INFO"
                                                                                    
                                                                                        # Email Processing
                                                                                            max_email_size: int = 10 * 1024 * 1024  # 10MB
                                                                                                batch_size: int = 10
                                                                                                    processing_timeout: int = 300  # 5 minutes
                                                                                                        
                                                                                                            # Model Settings
                                                                                                                model_name: str = "gpt-4"
                                                                                                                    temperature: float = 0.7
                                                                                                                        max_tokens: int = 2000
                                                                                                                            
                                                                                                                                # Calendar Settings
                                                                                                                                    calendar_id: str = "primary"
                                                                                                                                        timezone: str = "UTC"
                                                                                                                                            
                                                                                                                                                class Config:
                                                                                                                                                        env_file = ".env"
                                                                                                                                                                case_sensitive = False

                                                                                                                                                                settings = Settings()