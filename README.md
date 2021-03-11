# Saúde, Educação e Economia no RN

Endereço dos painéis criados: [Resultados Parciais (metade das cidades)](https://app.powerbi.com/view?r=eyJrIjoiNjljNTlmZTItMzM0OC00ZjI0LTk0OWUtNTMxN2NhYzJjZmY5IiwidCI6ImRjYmYyYTFmLTk1MzItNGQ1Ni1hYzQxLTU2MTVlMzhlNTBiNyJ9)

# Como usar

## Este projeto consiste de:

1. Código em python para coletar as informações dos municípios, o qual faz a maior parte das transformações;
2. Paineis do Power BI que fazem algumas transformações nos dados, relacionam as diferentes tabelas e geram gráficos interativos para analisar essas informações;

## Requisitos

Python 3.8 e Power BI. Os pacotes Python necessários estão descritos no arquivo "requirements.txt".

## Como Executar

Executar os seguintes scripts em sequência:

1. "listar_cidades.py": Lista as cidades do RN, baseado na wikipedia;
2. "minerar_dados_cidades.py": Acessa tabelas do IBGE Cidades para criar tabelas sobre saúde, economia e educação;
3. "modelagem_estrela.py": Utiliza modelagem estrela para conectar as colunas relevantes das tabelas criadas anteriormente, dando origem ao arquivo "output/city_data/data_warehouse.tsv";

# Descrição do Projeto
Integrantes do Grupo:
- Pitágoras Alves
- João Matias

Tema: Economia, saúde e educação nos múnicipios do RN

## 1. Domínio da aplicação:

Dados do IBGE Cidades, obtidos por webscraping. Tabelas:
- Tabela de produto interno bruto
- Tabela de população residente
- Tabela de educação
- Tabela de sinopse do censo escolar
- Tabela de serviços de saúde

(dados salvos em arquivos .TSV)

Modelagem dos dados: Modelagem Estrela, para gerar uma única tabela fato 
	com dados de cada cidade.

## 2. Perguntas a serem respondidas:
- Levando em conta a população local, quais cidades:
	- Possuem uma população com maior nível de educação?
	- Possuem mais unidades de saúde e/ou leitos de UTI?
- Levando em conta a população da cidade, quais tem uma porcentagem maior da 
	população frequentando a escola?
- Quais regiões do RN possuem PIB per capita mais alto? Quais tem menor PIB?

## 3. Cliente: público geral
As informações são de interesse ao público geral, então os resultados serão 
	disponibilizados num repositório público.

## 4. Quais gráficos serão utilizados?
- Mapa Coroplético
- Gráfico de dispersão
- Cartão
- Gráfico de barras