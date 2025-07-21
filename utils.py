import json
import pandas as pd
import os
from typing import List, Dict, Any
from pathlib import Path
from models import Imovel, ResultadoScraping
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def criar_diretorio_output(output_dir: str) -> Path:
    """Cria o diretório de output se não existir"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Diretório de output criado/verificado: {path.absolute()}")
    return path


def limpar_preco(preco_str: str) -> float:
    """Limpa e converte string de preço para float"""
    if not preco_str:
        return None
    
    import re
    
    # Remove todos os caracteres exceto dígitos, pontos e vírgulas
    preco_limpo = re.sub(r'[^\d,.]', '', str(preco_str))
    
    if not preco_limpo:
        return None
    
    # Padrões brasileiros mais comuns:
    # 300.000,00 -> 300000.00
    # 1.200.000,50 -> 1200000.50
    # 450000 -> 450000
    # 350.000 -> 350000
    
    # Se termina com ,XX (centavos), converte vírgula para ponto
    if re.match(r'.*,\d{1,2}$', preco_limpo):
        # Substitui todos os pontos (separadores de milhares) por nada
        # e a vírgula (separador decimal) por ponto
        preco_limpo = preco_limpo.replace('.', '').replace(',', '.')
    else:
        # Remove todas as vírgulas e pontos exceto o último ponto (se houver)
        # ou converte tudo para um número inteiro
        preco_limpo = preco_limpo.replace(',', '').replace('.', '')
    
    try:
        return float(preco_limpo)
    except ValueError:
        logger.warning(f"Não foi possível converter preço: {preco_str}")
        return None


def extrair_numero(texto: str) -> int:
    """Extrai primeiro número inteiro de uma string"""
    if not texto:
        return None
    
    import re
    numeros = re.findall(r'\d+', str(texto))
    if numeros:
        return int(numeros[0])
    return None


def processar_dados_brutos(dados_brutos: Dict[str, Any]) -> List[Imovel]:
    """Processa dados brutos do Firecrawl para objetos Imovel"""
    imoveis = []
    
    if 'imoveis' in dados_brutos:
        for item in dados_brutos['imoveis']:
            try:
                # Processa o preço
                preco = None
                if 'preco' in item:
                    preco = limpar_preco(item['preco'])
                
                # Processa área
                area = None
                if 'area' in item:
                    area = extrair_numero(item['area'])
                
                # Processa quartos, banheiros, vagas
                quartos = extrair_numero(item.get('quartos'))
                banheiros = extrair_numero(item.get('banheiros'))
                vagas = extrair_numero(item.get('vagas'))
                
                # Cria o objeto Imovel
                imovel = Imovel(
                    titulo=item.get('titulo', ''),
                    endereco=item.get('endereco'),
                    preco=preco,
                    area=area,
                    quartos=quartos,
                    banheiros=banheiros,
                    vagas=vagas,
                    descricao=item.get('descricao'),
                    caracteristicas=item.get('caracteristicas', []),
                    link=item.get('link'),
                    imagens=item.get('imagens', []),
                    codigo_imovel=item.get('codigo_imovel'),
                    imobiliaria=item.get('imobiliaria')
                )
                
                imoveis.append(imovel)
                
            except Exception as e:
                logger.error(f"Erro ao processar imóvel: {e}")
                logger.debug(f"Dados do imóvel com erro: {item}")
                continue
    
    return imoveis


def salvar_json(resultado: ResultadoScraping, output_dir: Path, filename: str = "imoveis.json"):
    """Salva os dados em formato JSON"""
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(resultado.dict(), f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"Dados salvos em JSON: {filepath.absolute()}")


def salvar_csv(resultado: ResultadoScraping, output_dir: Path, filename: str = "imoveis.csv"):
    """Salva os dados em formato CSV"""
    filepath = output_dir / filename
    
    # Converte lista de imóveis para DataFrame
    dados_dict = []
    for imovel in resultado.imoveis:
        imovel_dict = imovel.dict()
        # Converte listas para strings para o CSV
        imovel_dict['caracteristicas'] = '; '.join(imovel_dict.get('caracteristicas', []))
        imovel_dict['imagens'] = '; '.join([str(img) for img in imovel_dict.get('imagens', [])])
        dados_dict.append(imovel_dict)
    
    df = pd.DataFrame(dados_dict)
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    logger.info(f"Dados salvos em CSV: {filepath.absolute()}")


def log_estatisticas(resultado: ResultadoScraping):
    """Log estatísticas do scraping"""
    logger.info(f"=== ESTATÍSTICAS DO SCRAPING ===")
    logger.info(f"Total de imóveis extraídos: {resultado.total_extraidos}")
    logger.info(f"URL de origem: {resultado.url_origem}")
    logger.info(f"Data do scraping: {resultado.data_scraping}")
    
    if resultado.imoveis:
        # Estatísticas de preços
        precos = [i.preco for i in resultado.imoveis if i.preco]
        if precos:
            logger.info(f"Preço médio: R$ {sum(precos)/len(precos):,.2f}")
            logger.info(f"Preço mínimo: R$ {min(precos):,.2f}")
            logger.info(f"Preço máximo: R$ {max(precos):,.2f}")
        
        # Estatísticas de área
        areas = [i.area for i in resultado.imoveis if i.area]
        if areas:
            logger.info(f"Área média: {sum(areas)/len(areas):.1f} m²")
        
        # Distribuição de quartos
        quartos = [i.quartos for i in resultado.imoveis if i.quartos]
        if quartos:
            from collections import Counter
            dist_quartos = Counter(quartos)
            logger.info(f"Distribuição de quartos: {dict(dist_quartos)}")


def validar_dados(imoveis: List[Imovel]) -> List[Imovel]:
    """Valida e filtra dados inválidos"""
    imoveis_validos = []
    
    for imovel in imoveis:
        # Remove imóveis sem título (obrigatório)
        if not imovel.titulo or imovel.titulo.strip() == '':
            logger.warning("Imóvel descartado por não ter título")
            continue
        
        # Remove duplicatas baseado no título e link
        duplicata = False
        for valido in imoveis_validos:
            if (valido.titulo == imovel.titulo and 
                valido.link == imovel.link):
                duplicata = True
                break
        
        if duplicata:
            logger.warning(f"Imóvel duplicado descartado: {imovel.titulo}")
            continue
        
        imoveis_validos.append(imovel)
    
    logger.info(f"Dados validados: {len(imoveis_validos)} imóveis válidos de {len(imoveis)} extraídos")
    return imoveis_validos