from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


class Imovel(BaseModel):
    """Modelo de dados para um imóvel extraído do scraping"""
    
    titulo: str = Field(..., description="Título do anúncio")
    endereco: Optional[str] = Field(None, description="Endereço/Localização do imóvel")
    preco: Optional[float] = Field(None, description="Preço do imóvel")
    area: Optional[float] = Field(None, description="Área em metros quadrados")
    quartos: Optional[int] = Field(None, description="Número de quartos")
    banheiros: Optional[int] = Field(None, description="Número de banheiros")
    vagas: Optional[int] = Field(None, description="Número de vagas de garagem")
    descricao: Optional[str] = Field(None, description="Descrição do imóvel")
    caracteristicas: Optional[List[str]] = Field(default_factory=list, description="Lista de características/amenidades")
    link: Optional[HttpUrl] = Field(None, description="Link do anúncio")
    imagens: Optional[List[HttpUrl]] = Field(default_factory=list, description="URLs das imagens")
    codigo_imovel: Optional[str] = Field(None, description="Código identificador do imóvel")
    imobiliaria: Optional[str] = Field(None, description="Nome da imobiliária ou corretor")
    data_extracao: datetime = Field(default_factory=datetime.now, description="Data e hora da extração")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }


class ResultadoScraping(BaseModel):
    """Modelo para o resultado completo do scraping"""
    
    imoveis: List[Imovel] = Field(default_factory=list)
    total_extraidos: int = Field(0, description="Total de imóveis extraídos")
    url_origem: str = Field(..., description="URL de origem do scraping")
    data_scraping: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }