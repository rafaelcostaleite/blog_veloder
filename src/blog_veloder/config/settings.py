import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configurações globais do projeto"""
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # Diretórios
    DATA_DIR = "data"
    OUTPUT_DIR = "output"
    
    # Configurações dos modelos
    DEFAULT_MODEL = "gpt-4-turbo-preview"
    TEMPERATURE = 0.7
    
    @classmethod
    def validate_config(cls):
        """Valida se todas as configurações necessárias estão presentes"""
        required_vars = ["OPENAI_API_KEY", "SERPER_API_KEY"]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente ausentes: {missing_vars}")
        
        return True