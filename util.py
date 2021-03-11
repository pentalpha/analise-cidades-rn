# -*- coding: utf-8 -*-
"""
Funções de uso geral para as funções de ETL neste projeto.
"""
from unicodedata import normalize
from threading import Thread

def remover_acentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

def run_threads(args, func):
    threads = list()
    infos = []
    first=True
    for arg_set in args:
        thread = Thread(target=func, args=(arg_set, infos, first))
        threads.append(thread)
        first = False
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return infos