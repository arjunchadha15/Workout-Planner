"""
Configuration management for the application.
Loads environment variables and provides centralized config access.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the same directory as this config file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')  # Default to GPT-4o
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./repple.db')
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Exercise Selection Parameters
    MAX_EXERCISES_PER_SESSION = int(os.getenv('MAX_EXERCISES_PER_SESSION', '8'))
    MIN_EXERCISES_PER_SESSION = int(os.getenv('MIN_EXERCISES_PER_SESSION', '4'))
    
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        
        if not cls.OPENAI_API_KEY.startswith('sk-'):
            raise ValueError(
                "OPENAI_API_KEY appears to be invalid. "
                "It should start with 'sk-'"
            )
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI-specific configuration as a dictionary"""
        return {
            'api_key': cls.OPENAI_API_KEY,
            'model': cls.OPENAI_MODEL,
            'max_tokens': cls.OPENAI_MAX_TOKENS,
            'temperature': cls.OPENAI_TEMPERATURE,
        }


# Validate config on import (optional - comment out if you want lazy validation)
# Config.validate()
