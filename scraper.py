#!/usr/bin/env python3
"""
Scraper de Imóveis - João Pessoa
Script principal para extração de dados de apartamentos usando Firecrawl
"""

import argparse
import sys
import time
from datetime import datetime
from typing import List

from firecrawl import FirecrawlApp
from config import Config
from models import Imovel, ResultadoScraping
from utils import (
    criar_diretorio_output, 
    processar_dados_brutos, 
    salvar_json, 
    salvar_csv,
    log_estatisticas,
    validar_dados,
    logger
)


class ScraperImoveis:
    """Classe principal para o scraping de imóveis"""
    
    def __init__(self, api_key: str):
        """Inicializa o scraper com a API key do Firecrawl"""
        self.app = FirecrawlApp(api_key=api_key)
        
    def executar_crawl(self, url: str, limit: int = None) -> dict:
        """Executa o crawl da URL especificada"""
        logger.info(f"Iniciando crawl da URL: {url}")
        logger.info(f"Limite de páginas: {limit or Config.DEFAULT_LIMIT}")
        
        # Configurações do crawl
        crawl_config = Config.CRAWL_CONFIG.copy()
        if limit:
            crawl_config["limit"] = limit
        
        try:
            # Executa o crawl
            crawl_status = self.app.crawl_url(
                url=url,
                params=crawl_config,
                wait_until_done=True,
                timeout=300  # 5 minutos timeout
            )
            
            logger.info(f"Crawl concluído. Status: {crawl_status.get('status', 'unknown')}")
            return crawl_status
            
        except Exception as e:
            logger.error(f"Erro durante o crawl: {e}")
            raise
    
    def extrair_dados_estruturados(self, crawl_result: dict) -> dict:
        """Extrai dados estruturados usando LLM do Firecrawl"""
        logger.info("Iniciando extração de dados estruturados")
        
        if 'data' not in crawl_result:
            raise ValueError("Resultado do crawl não contém dados")
        
        # Prepara o conteúdo para extração
        urls_crawled = []
        for item in crawl_result['data']:
            if 'markdown' in item:
                urls_crawled.append({
                    'url': item.get('url', ''),
                    'content': item['markdown']
                })
        
        logger.info(f"Extraindo dados de {len(urls_crawled)} páginas crawled")
        
        # Prompt para extração de dados de imóveis
        extraction_prompt = """
        Extraia informações de apartamentos/imóveis à venda do conteúdo fornecido.
        Para cada imóvel encontrado, extraia:
        - titulo: título do anúncio
        - endereco: endereço completo ou localização
        - preco: preço de venda (apenas números)
        - area: área em metros quadrados (apenas números)
        - quartos: número de quartos/dormitórios
        - banheiros: número de banheiros
        - vagas: número de vagas de garagem
        - descricao: descrição detalhada do imóvel
        - caracteristicas: lista de características e amenidades
        - link: URL da página do imóvel
        - codigo_imovel: código ou referência do imóvel
        - imobiliaria: nome da imobiliária ou corretor
        
        Retorne apenas imóveis reais (não propagandas ou outros conteúdos).
        """
        
        try:
            # Extrai dados estruturados
            extracted_data = self.app.extract(
                urls=[item['url'] for item in urls_crawled],
                schema=Config.EXTRACTION_SCHEMA,
                prompt=extraction_prompt
            )
            
            logger.info("Extração de dados estruturados concluída")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Erro durante a extração: {e}")
            raise
    
    def processar_resultado(self, extracted_data: dict, url_origem: str) -> ResultadoScraping:
        """Processa o resultado extraído em objetos estruturados"""
        logger.info("Processando dados extraídos")
        
        # Processa os dados brutos
        imoveis_brutos = processar_dados_brutos(extracted_data)
        
        # Valida os dados
        imoveis_validos = validar_dados(imoveis_brutos)
        
        # Cria resultado estruturado
        resultado = ResultadoScraping(
            imoveis=imoveis_validos,
            total_extraidos=len(imoveis_validos),
            url_origem=url_origem,
            data_scraping=datetime.now()
        )
        
        logger.info(f"Processamento concluído: {resultado.total_extraidos} imóveis válidos")
        return resultado


def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description="Scraper de Imóveis - João Pessoa")
    parser.add_argument(
        "--limit", 
        type=int, 
        default=Config.DEFAULT_LIMIT,
        help=f"Número máximo de páginas para crawl (padrão: {Config.DEFAULT_LIMIT})"
    )
    parser.add_argument(
        "--output-dir", 
        default=Config.DEFAULT_OUTPUT_DIR,
        help=f"Diretório para salvar os arquivos (padrão: {Config.DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--formato", 
        default="json,csv",
        help="Formatos de saída separados por vírgula (padrão: json,csv)"
    )
    parser.add_argument(
        "--url", 
        default=Config.DEFAULT_URL,
        help=f"URL inicial para o crawl (padrão: {Config.DEFAULT_URL})"
    )
    
    args = parser.parse_args()
    
    # Valida configuração
    if not Config.validate_api_key():
        logger.error("API Key do Firecrawl não configurada!")
        logger.error("Configure a variável FIRECRAWL_API_KEY no arquivo .env")
        sys.exit(1)
    
    # Cria diretório de output
    output_dir = criar_diretorio_output(args.output_dir)
    
    # Formatos de saída
    formatos = [f.strip().lower() for f in args.formato.split(',')]
    
    logger.info("=== INICIANDO SCRAPING DE IMÓVEIS ===")
    logger.info(f"URL: {args.url}")
    logger.info(f"Limite: {args.limit}")
    logger.info(f"Output: {output_dir.absolute()}")
    logger.info(f"Formatos: {formatos}")
    
    try:
        # Inicializa o scraper
        scraper = ScraperImoveis(Config.FIRECRAWL_API_KEY)
        
        # Executa o crawl
        crawl_result = scraper.executar_crawl(args.url, args.limit)
        
        # Extrai dados estruturados
        extracted_data = scraper.extrair_dados_estruturados(crawl_result)
        
        # Processa resultado
        resultado = scraper.processar_resultado(extracted_data, args.url)
        
        # Salva os dados
        if 'json' in formatos:
            salvar_json(resultado, output_dir)
        
        if 'csv' in formatos:
            salvar_csv(resultado, output_dir)
        
        # Log estatísticas
        log_estatisticas(resultado)
        
        logger.info("=== SCRAPING CONCLUÍDO COM SUCESSO ===")
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro durante o scraping: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()