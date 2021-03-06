# -*- coding: utf-8 -*-
"""
Funções para minerar nomes de cidades do RN, seus PIBs e populações 
a partir da Wikipedia e do IBGE. Utiliza as bibliotecas BeautifulSoup 
e Selenium.

Mapa de dados raspados do IBGE:

Produto Interno Bruto dos Municípios: PIB a preços correntes > Série revisada
Censo - Sinopse: População residente
Censo - Educação (23/22469): Frequência à escola ou creche> Frequentavam e Nunca frequentou,
    nível de instrução>
        Sem instrução e fundamental incompleto
        Fundamental completo e médio incompleto 
        Médio completo e superior incompleto 
        Superior completo

Censo escolar - sinopse (13/78117): 
    Matrículas >
        Ensino infantil 
        Ensino fundamental
        Ensino médio

Serviços de saúde (32/28163):
    Esfera administrativa > Público
    Número de leitos para internação > Esfera administrativa > Público

"""

import time, os, logging, sys
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import geckodriver_autoinstaller
geckopath = geckodriver_autoinstaller.install()

from util import run_threads

from configurations import configurations

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.ERROR, 
                    stream=sys.stdout,
                    format=logformat, 
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) '+
           'Gecko/20100101 Firefox/85.0 Accept: */*'}

options = Options()
options.headless = True

scraping_conf = configurations['SCRAPING']
wikipedia_cities = scraping_conf['wikipedia_cidades']
ibge_base = scraping_conf['ibge_rn']
research_codes = {
    'PIB': "/38/46996",
    'POP': "/23/27652",
    'EDUCACAO': "/23/22469",
    'MATRICULAS': "/13/78117",
    'SAUDE': "/32/28163"
    }
properties = list(research_codes.keys())

output_dir = os.path.join(str(os.path.dirname(__file__)), "output")
city_data_dir = os.path.join(output_dir, "city_data")
city_names_path = str(os.path.join(city_data_dir, 'city_names.txt'))
city_lists_dir = os.path.join(city_data_dir, "city_lists")
if not os.path.exists(city_data_dir):
    os.mkdir(city_data_dir)
    
cols = ['PIB', 'PIB_ANO',
        'POP_RESIDENTE', 'POP_ANO',
        'FREQUENTANDO_ESCOLA', 'NAO_FREQUENTANDO_ESCOLA',
        'SEM_INSTRUCAO', 'NIVEL_FUNDAMENTAL',
        'NIVEL_MEDIO', 'NIVEL_SUPERIOR',
        'EDUCACAO_ANO', 'MATRICULAS_INFANTIL',
        'MATRICULAS_FUNDAMENTAL', 'MATRICULAS_MEDIO',
        'MATRICULAS_ANO',
        'ESTABELECIMENTOS_SAUDE_PUBLICOS',
        'LEITOS_PARA_INTERNAÇÃO_PUBLICOS',
        'SAUDE_ANO']
#%%


    
def ibge_url(city,data_to_get):
    base = ibge_base+city+"/pesquisa"
    base += research_codes[data_to_get]
    return base

def get_last_year(html):
    bs = BeautifulSoup(html, features="lxml")
    year_selectors = bs.find_all("select",{"class":"select-ano"})
    if len(year_selectors) > 0:
        return year_selectors[0].find_all("option")[0].contents[0]
    else:
        return None

def pib_extractor(tables):
    if len(tables) > 0:
        return {"PIB": float(tables[0][1].tolist()[1])*1000}
    return {"PIB": None}

def sinopse_extractor(tables):
    if len(tables) > 0:
        table = tables[0]
        pop_lines = table[table[0] == "População residente (pessoas)"]
        if len(pop_lines) > 0:
            pop = pop_lines[1].tolist()[0]
            return {"POP_RESIDENTE": pop}
    return {"POP_RESIDENTE": None}

def educ_extractor(tables):
    if len(tables) > 0:
        table = tables[0]
        
        freq_lines = table[table[0] == 'Frequentavam (pessoas)']
        frequentam = freq_lines[1].tolist()[0] if len(freq_lines) > 0 else None
        n_freq_lines = table[table[0] == 'Não frequentavam (pessoas)']
        n_frequentam = n_freq_lines[1].tolist()[0] if len(n_freq_lines) > 0 else None
        no_instruction_lines = table[table[0] == 'Sem instrução e fundamental incompleto (pessoas)']
        no_instruction = no_instruction_lines[1].tolist()[0] if len(no_instruction_lines) > 0 else None
        fund_lines = table[table[0] == 'Fundamental completo e médio incompleto (pessoas)']
        fund = fund_lines[1].tolist()[0] if len(fund_lines) > 0 else None
        med_lines = table[table[0] == 'Médio completo e superior incompleto (pessoas)']
        med = med_lines[1].tolist()[0] if len(med_lines) > 0 else None
        sup_lines = table[table[0] == 'Superior completo (pessoas)']
        sup = sup_lines[1].tolist()[0] if len(sup_lines) > 0 else None
        
        return {'FREQUENTANDO_ESCOLA': frequentam, 'NAO_FREQUENTANDO_ESCOLA': n_frequentam,
                'SEM_INSTRUCAO': no_instruction, 'NIVEL_FUNDAMENTAL': fund,
                'NIVEL_MEDIO': med, 'NIVEL_SUPERIOR': sup}
    return {'FREQUENTANDO_ESCOLA': None, 'NAO_FREQUENTANDO_ESCOLA': None,
            'SEM_INSTRUCAO': None, 'NIVEL_FUNDAMENTAL': None,
            'NIVEL_MEDIO': None, 'NIVEL_SUPERIOR': None}

def school_extractor(tables):
    if len(tables) > 0:
       table = tables[0]
       tem_matriculas = len(table[table[0] == 'Matrículas']) > 0
       if tem_matriculas:
           infantil = table[table[0] == 'Ensino infantil (matrículas)'][1].tolist()[0]
           fundamental = table[table[0] == 'Ensino fundamental (matrículas)'][1].tolist()[0]
           medio = table[table[0] == 'Ensino médio (matrículas)'][1].tolist()[0]
           return {'MATRICULAS_INFANTIL': infantil, 
                   'MATRICULAS_FUNDAMENTAL': fundamental,
                   'MATRICULAS_MEDIO': medio}
    
    return {'MATRICULAS_INFANTIL': None,
            'MATRICULAS_FUNDAMENTAL': None,
            'MATRICULAS_MEDIO': None}

def health_extractor(tables):
    estabelecimentos = None
    leitos_publicos = None
    if len(tables) > 0:
        table = tables[0]
        leitos_str = ('Número de leitos para internação em estabelecimentos '
                      +'de saúde (leitos)')
        tem_leitos = len(table[table[0] == leitos_str]) > 0
        if tem_leitos:
            leitos_publicos = table[table[0] == 'Público (leitos)'][1].tolist()[-1]
        estabelecimentos_lines = table[table[0] == 'Público (estabelecimentos)']
        if len(estabelecimentos_lines) > 0:
            estabelecimentos = estabelecimentos_lines[1].tolist()[0]
    return{'ESTABELECIMENTOS_SAUDE_PUBLICOS': estabelecimentos,
           'LEITOS_PARA_INTERNAÇÃO_PUBLICOS': leitos_publicos}

extractors = {
        'PIB': pib_extractor,
        'POP': sinopse_extractor,
        'EDUCACAO': educ_extractor,
        'MATRICULAS': school_extractor,
        'SAUDE': health_extractor
        }

def scrap_city(driver, city, props=properties):
    table_data = {}
    for prop in props:
        new_row = {}
        new_row['cidade'] = city
        current_tries = 4
        url = ibge_url(city, prop)
        driver.get(url)
        time.sleep(3)
        elem = driver.find_element_by_xpath("//*")
        html = elem.get_attribute('innerHTML')
        tables = []
        while len(tables) == 0 and current_tries > 0:
            try:
                tables = pd.read_html(html, decimal=',', thousands='.')
            except Exception as ex:
                current_tries -= 1
                logger.warning("Failed to load tables from " 
                               + url + " (" + str(ex) + ")"
                               +". Remaining tries: " 
                               + str(current_tries))
                time.sleep(3.5)
        outs = extractors[prop](tables)
        for label, data in outs.items():
            new_row[label] = data
        new_row['ANO'] = get_last_year(html)
        table_data[prop] = new_row
        #print("Got", prop, "from", city)
    return table_data

def scan_city_list(cities, outputs, first):
    driver = webdriver.Firefox(options=options)
    for city in cities:
        out = scrap_city(driver, city)
        outputs.append(out)
    driver.quit()

def read_cities(city_list_path=city_names_path):
    return [line.rstrip("\n").split()[0] 
            for line in open(city_list_path,'r').readlines()]

def read_city_data(path):
    lines = {}
    with open(path,'r') as stream:
        header = stream.readline().rstrip("\n").split('\t')
        for line in stream:
            cells = line.rstrip("\n").split('\t')
            lines[cells[0]] = {header[i]: cells[i] for i in range(1,len(cells))}
    return lines

def write_city_data(path, data):
    with open(path,'w') as stream:
        line = 'cidade'+'\t'+'\t'.join(cols)+'\n'
        stream.write(line)
        for city, cells in data.items():
            line = city+'\t'+'\t'.join([cells[col] for col in cols])+'\n'
            stream.write(line)

#%%
    
def separate_dicts(result_dicts):
    row_groups = {}
    for city_data in result_dicts:
        for data_type in city_data.keys():
            if not data_type in row_groups:
                row_groups[data_type] = []
            row_groups[data_type].append(city_data[data_type])
    dfs = {}
    for data_type, rows in row_groups.items():
        new_df = pd.DataFrame(rows)
        dfs[data_type] = new_df
    return dfs

def get_city_lists():
    lists = []
    for i in range(100):
        p = os.path.join(city_lists_dir,str(i)+".tsv")
        if os.path.exists(p):
            lists.append(p)
    return lists

def scrap_city_list(city_list_file, processes):
    if not os.path.exists(city_list_file + ".OK"):
        print("Scraping", city_list_file)
        cities_rn = read_cities(city_list_path=city_list_file)
        city_chunks = [x.tolist() 
                       for x in np.array_split(cities_rn, processes)]
        result_dicts = run_threads(city_chunks, scan_city_list)
        dfs = separate_dicts(result_dicts)
        if len(dfs.keys()) == 5:
            all_correct_lens = True
            for name, df in dfs.items():
                df.set_index('cidade').to_csv(city_list_file+"."+name+'.tsv',
                          sep='\t')
                all_correct_lens = (all_correct_lens 
                                    and len(df) == len(cities_rn))
            if all_correct_lens:
                open(city_list_file + ".OK", 'w').write("okay")
            else:
                for name, df in dfs.items():
                    path = city_list_file+"."+name+'.tsv'
                    if os.path.exists(path):
                        os.remove(path)

#editar número de processos e número de cidades (ou todas as cidades) aqui:
def scrap_cities(processes=4):
    city_lists = get_city_lists()
    for city_list in tqdm(city_lists):
        scrap_city_list(city_list, processes)

#scrap_cities()
#%%
def join_downloaded_data():
    city_lists = get_city_lists()
    dfs = {data_type: [] for data_type in research_codes.keys()}
    for city_list in tqdm(city_lists):
        if os.path.exists(city_list + ".OK"):
            for data_type in research_codes.keys():
                df_path = city_list + "." + data_type + ".tsv"
                dfs[data_type].append(pd.read_csv(
                    df_path, sep='\t', index_col=0))
    
    for data_type, df_list in dfs.items():
        df = df_list[0]
        for other_df in df_list[1:]:
            df = df.append(other_df)
        df.to_csv(city_data_dir+"/"+data_type+".tsv", sep='\t')

join_downloaded_data()