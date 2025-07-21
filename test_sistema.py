#!/usr/bin/env python3
"""
Teste do Sistema de Scraping
Valida se todos os componentes estão funcionando corretamente
"""

import json
import pandas as pd
from pathlib import Path

from models import Imovel, ResultadoScraping
from utils import (
    limpar_preco,
    extrair_numero,
    validar_dados,
    log_estatisticas,
    logger
)
from config import Config


def test_models():
    """Testa os modelos de dados"""
    logger.info("Testando modelos de dados...")
    
    # Cria um imóvel de teste
    imovel = Imovel(
        titulo="Apartamento Teste",
        endereco="Rua Teste, 123",
        preco=300000.0,
        area=80.0,
        quartos=2,
        banheiros=1,
        vagas=1
    )
    
    assert imovel.titulo == "Apartamento Teste"
    assert imovel.preco == 300000.0
    logger.info("✅ Modelos funcionando corretamente")


def test_utils():
    """Testa funções utilitárias"""
    logger.info("Testando funções utilitárias...")
    
    # Testa limpeza de preços
    assert limpar_preco("R$ 300.000,00") == 300000.0
    assert limpar_preco("450000") == 450000.0
    assert limpar_preco("R$ 1.200.000,50") == 1200000.50
    assert limpar_preco("350000") == 350000.0
    
    # Testa extração de números
    assert extrair_numero("3 quartos") == 3
    assert extrair_numero("120 m²") == 120
    assert extrair_numero("sem número") is None
    
    logger.info("✅ Funções utilitárias funcionando corretamente")


def test_config():
    """Testa configurações"""
    logger.info("Testando configurações...")
    
    assert Config.DEFAULT_URL == "https://www.imoveisjoaopessoa.com.br"
    assert Config.DEFAULT_LIMIT == 50
    assert "imoveis" in Config.EXTRACTION_SCHEMA["properties"]
    
    logger.info("✅ Configurações carregadas corretamente")


def test_output_files():
    """Verifica se os arquivos de saída foram gerados"""
    logger.info("Verificando arquivos de saída...")
    
    output_dir = Path("./output")
    json_file = output_dir / "imoveis.json"
    csv_file = output_dir / "imoveis.csv"
    
    assert json_file.exists(), "Arquivo JSON não encontrado"
    assert csv_file.exists(), "Arquivo CSV não encontrado"
    
    # Valida estrutura do JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert "imoveis" in data
    assert "total_extraidos" in data
    assert len(data["imoveis"]) > 0
    
    # Valida CSV
    df = pd.read_csv(csv_file)
    assert len(df) > 0
    assert "titulo" in df.columns
    assert "preco" in df.columns
    
    logger.info("✅ Arquivos de saída válidos")


def main():
    """Executa todos os testes"""
    logger.info("=== INICIANDO TESTES DO SISTEMA ===")
    
    try:
        test_config()
        test_models()
        test_utils()
        test_output_files()
        
        logger.info("=== TODOS OS TESTES PASSARAM ===")
        logger.info("✅ Sistema funcionando corretamente!")
        
    except Exception as e:
        logger.error(f"❌ Teste falhou: {e}")
        raise


if __name__ == "__main__":
    main()