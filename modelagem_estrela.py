# -*- coding: utf-8 -*-
import pandas as pd

df_paths = {name: 'output/city_data/'+name+".tsv"
            for name in ['EDUCACAO', 
                         'MATRICULAS', 
                         'PIB', 
                         'POP', 
                         'SAUDE']}

dfs = {name: pd.read_csv(path, sep='\t', index_col=0) 
       for name, path in df_paths.items()}

dfs_no_year = [df.drop(columns=['ANO'], axis=1) for name, df in dfs.items()]

base_df = dfs_no_year[0]

for i in range(1,len(dfs_no_year)):
    base_df = base_df.join(dfs_no_year[i])
for column in base_df.columns:
    base_df[column] = base_df[column].astype('Int64')
    base_df[column] = base_df[column].fillna(int(base_df[column].mean())) 
base_df.to_csv("output/city_data/data_warehouse.tsv", sep='\t')
