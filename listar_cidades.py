# -*- coding: utf-8 -*-
import time, os, logging, sys
import pandas as pd
from tqdm import tqdm
import numpy as np
from bs4 import BeautifulSoup
from util import remover_acentos
import shutil
from configurations import configurations

logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.ERROR, 
                    stream=sys.stdout,
                    format=logformat, 
                    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

aliases = {"-": ['_',' '],
           "a": ['â','ã'],
           "o": ['ô','õ'],
           'c': ['ç'],
           '': ["'"]}
renamed_cities = {'assu': 'acu',
                  'arez': 'ares',
                  'boa-saude': 'januario-cicco'}

scraping_conf = configurations['SCRAPING']
wikipedia_cities = scraping_conf['wikipedia_cidades']
output_dir = os.path.join(str(os.path.dirname(__file__)), "output")
city_data_dir = os.path.join(output_dir, "city_data")
city_lists_dir = os.path.join(city_data_dir, "city_lists")
city_names_path = str(os.path.join(city_data_dir, 'city_names.txt'))
if not os.path.exists(city_data_dir):
    os.mkdir(city_data_dir)
if os.path.exists(city_lists_dir):
    shutil.rmtree(city_lists_dir)
os.mkdir(city_lists_dir)
    
def parse_str(names):
    names = names.lower()
    for target, to_replace in aliases.items():
        for rp in to_replace:
            names = names.replace(rp,target)
    ascii_str = remover_acentos(names)
    return ascii_str

def scrap_municipios_wikipedia():
    tables = pd.read_html(wikipedia_cities)
    mun_tables = tables[0]
    cities = mun_tables["Município"].tolist()
    parsed_cities = [parse_str(city) for city in tqdm(cities)]
    for i in range(len(parsed_cities)):
        for old, new in renamed_cities.items():
            if parsed_cities[i] == old:
                parsed_cities[i] = new
    original_and_new = [parsed_cities[i]+"\t"+cities[i]
                        for i in range(len(parsed_cities))]
    return original_and_new

def scrap_city_names_wikipedia():
    cities_rn = scrap_municipios_wikipedia()
    open(city_names_path,'w').write("\n".join(cities_rn)+"\n")
    
    city_chunks = [x.tolist() for x in np.array_split(cities_rn, 30)]
    for i in range(len(city_chunks)):
        open(os.path.join(city_lists_dir, str(i)+".tsv"), 'w').write(
            "\n".join(city_chunks[i])+"\n")
        
scrap_city_names_wikipedia()