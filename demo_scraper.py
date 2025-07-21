#!/usr/bin/env python3
"""
Scraper de Imóveis - Demo/Test Version
Gera dados de exemplo para demonstrar o funcionamento do sistema
"""

import json
import random
from datetime import datetime
from typing import List

from models import Imovel, ResultadoScraping
from utils import (
    criar_diretorio_output, 
    salvar_json, 
    salvar_csv,
    log_estatisticas,
    logger
)


def gerar_dados_exemplo() -> List[Imovel]:
    """Gera dados de exemplo para demonstração"""
    
    # Dados de exemplo realistas para João Pessoa
    titulos = [
        "Apartamento 3 quartos no Bessa com vista para o mar",
        "Cobertura duplex 4 quartos no Cabo Branco",
        "Apartamento novo 2 quartos em Manaíra",
        "Loft moderno 1 quarto no Centro Histórico",
        "Apartamento 3 quartos na Ponta do Seixas",
        "Duplex 4 quartos no Altiplano Cabo Branco",
        "Apartamento 2 quartos reformado no Bancários",
        "Cobertura 3 quartos no Portal do Sol",
        "Apartamento frente mar 3 quartos no Bessa",
        "Lançamento 2 quartos em Tambaú",
        "Apartamento 4 quartos na Torre",
        "Studio mobiliado em Cabo Branco",
        "Apartamento 3 quartos no Expedicionários",
        "Duplex 3 quartos na Praia de Intermares",
        "Apartamento 2 quartos no Valentina Figueiredo",
    ]
    
    enderecos = [
        "Av. Cabo Branco, 2500 - Cabo Branco",
        "Rua das Trincheiras, 150 - Bessa", 
        "Av. Gov. Flávio Ribeiro Coutinho, 800 - Manaíra",
        "Rua Duque de Caxias, 300 - Centro",
        "Av. Almirante Tamandaré, 1200 - Tambaú",
        "Rua Major Ciraulo, 450 - Torre",
        "Av. Presidente Epitácio Pessoa, 1800 - Bancários",
        "Rua José Américo de Almeida, 600 - Altiplano",
        "Av. João Maurício, 950 - Manaíra",
        "Rua Infante Dom Henrique, 200 - Cabo Branco",
        "Av. Ministro José Américo, 1500 - Expedicionários",
        "Rua Coronel José Pessoa, 350 - Bessa",
        "Av. Senador Ruy Carneiro, 1100 - Tambaú",
        "Rua Walfredo Macedo Brandão, 750 - Portal do Sol",
        "Av. Ruy Carneiro, 2200 - Manaíra",
    ]
    
    imobiliarias = [
        "Imóveis João Pessoa",
        "Cabo Branco Imóveis", 
        "Manaíra Properties",
        "Tambaú Real Estate",
        "Bessa Home",
        "JP Apartamentos",
        "Costa Dourada Imóveis",
        "Portal Imobiliário",
        "Mar Azul Properties",
        "Cidade Sol Imóveis"
    ]
    
    caracteristicas_opcoes = [
        "Piscina", "Academia", "Churrasqueira", "Playground", "Salão de festas",
        "Portaria 24h", "Elevador", "Garagem coberta", "Ar condicionado",
        "Varanda", "Vista para o mar", "Quintal", "Área gourmet",
        "Interfone", "TV a cabo", "Internet", "Mobiliado", "Semi-mobiliado"
    ]
    
    imoveis = []
    
    for i in range(15):  # Gera 15 imóveis de exemplo
        # Randomiza características
        quartos = random.choice([1, 2, 3, 4])
        banheiros = min(quartos, random.choice([1, 2, 3]))
        vagas = random.choice([1, 2, 3]) if random.random() > 0.2 else 0
        area = random.randint(45, 200)
        
        # Preço baseado na área e localização
        preco_base = area * random.uniform(3000, 8000)
        preco = round(preco_base + random.uniform(-50000, 100000), 2)
        
        # Seleciona características aleatórias
        num_caracteristicas = random.randint(3, 8)
        caracteristicas = random.sample(caracteristicas_opcoes, num_caracteristicas)
        
        # Gera URLs de exemplo
        link = f"https://www.imoveisjoaopessoa.com.br/imovel/{1000 + i}"
        imagens = [
            f"https://www.imoveisjoaopessoa.com.br/images/imovel_{1000 + i}_foto_{j}.jpg"
            for j in range(1, random.randint(3, 8))
        ]
        
        imovel = Imovel(
            titulo=random.choice(titulos),
            endereco=random.choice(enderecos),
            preco=preco,
            area=area,
            quartos=quartos,
            banheiros=banheiros,
            vagas=vagas,
            descricao=f"Excelente apartamento de {quartos} quartos com {area}m² em ótima localização. Imóvel em bom estado de conservação com acabamento de qualidade.",
            caracteristicas=caracteristicas,
            link=link,
            imagens=imagens,
            codigo_imovel=f"JP{1000 + i}",
            imobiliaria=random.choice(imobiliarias)
        )
        
        imoveis.append(imovel)
    
    return imoveis


def main():
    """Gera dados de exemplo e demonstra o funcionamento do sistema"""
    logger.info("=== DEMO - SCRAPING DE IMÓVEIS ===")
    logger.info("Gerando dados de exemplo...")
    
    # Cria diretório de output
    output_dir = criar_diretorio_output("./output")
    
    # Gera dados de exemplo
    imoveis_exemplo = gerar_dados_exemplo()
    
    # Cria resultado estruturado
    resultado = ResultadoScraping(
        imoveis=imoveis_exemplo,
        total_extraidos=len(imoveis_exemplo),
        url_origem="https://www.imoveisjoaopessoa.com.br (dados de exemplo)",
        data_scraping=datetime.now()
    )
    
    # Salva os dados
    salvar_json(resultado, output_dir)
    salvar_csv(resultado, output_dir)
    
    # Log estatísticas
    log_estatisticas(resultado)
    
    logger.info("=== DEMO CONCLUÍDO COM SUCESSO ===")
    logger.info(f"Arquivos gerados em: {output_dir.absolute()}")
    
    return resultado


if __name__ == "__main__":
    main()