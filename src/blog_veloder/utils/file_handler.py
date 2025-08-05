import json
import os
from typing import Dict, Any
from datetime import datetime

class FileHandler:
    """Utilitário para manipulação de arquivos"""
    
    @staticmethod
    def ensure_directory(directory: str) -> None:
        """Garante que o diretório existe"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def save_json(data: Dict[Any, Any], filepath: str) -> None:
        """Salva dados em formato JSON"""
        FileHandler.ensure_directory(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_json(filepath: str) -> Dict[Any, Any]:
        """Carrega dados de um arquivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_text(content: str, filepath: str) -> None:
        """Salva conteúdo de texto"""
        FileHandler.ensure_directory(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)