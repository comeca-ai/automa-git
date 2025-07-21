import os
from typing import List
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Config:
    """Configurações do projeto"""
    
    # API Firecrawl
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    
    # URLs e configurações de scraping
    DEFAULT_URL = "https://www.imoveisjoaopessoa.com.br"
    DEFAULT_LIMIT = 50
    DEFAULT_OUTPUT_DIR = "./output"
    DEFAULT_FORMATS = ["json", "csv"]
    
    # Configurações do Firecrawl
    CRAWL_CONFIG = {
        "limit": DEFAULT_LIMIT,
        "allowBackwardCrawling": False,
        "allowExternalContentLinks": False,
        "scrapeOptions": {
            "formats": ["markdown", "html"],
            "includeTags": ["title", "meta", "h1", "h2", "h3", "p", "div", "span", "a"],
            "excludeTags": ["script", "style", "nav", "footer", "header"],
            "onlyMainContent": True
        }
    }
    
    # Schema para extração de dados estruturados
    EXTRACTION_SCHEMA = {
        "type": "object",
        "properties": {
            "imoveis": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "titulo": {"type": "string"},
                        "endereco": {"type": "string"},
                        "preco": {"type": "number"},
                        "area": {"type": "number"},
                        "quartos": {"type": "integer"},
                        "banheiros": {"type": "integer"},
                        "vagas": {"type": "integer"},
                        "descricao": {"type": "string"},
                        "caracteristicas": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "link": {"type": "string", "format": "uri"},
                        "imagens": {
                            "type": "array",
                            "items": {"type": "string", "format": "uri"}
                        },
                        "codigo_imovel": {"type": "string"},
                        "imobiliaria": {"type": "string"}
                    },
                    "required": ["titulo"]
                }
            }
        }
    }
    
    @classmethod
    def validate_api_key(cls) -> bool:
        """Valida se a API key está configurada"""
        return cls.FIRECRAWL_API_KEY is not None and len(cls.FIRECRAWL_API_KEY.strip()) > 0