# raizen - anp fuel etl
# Developement of pipeline from Excel file by Python
# Date: 2021-07-09
# Author: Davison Rebechi
# v1

import os
import pandas as pd
import sqlite3

# Listing actual data directory
cwd = os.getcwd()

filename = cwd + '/data/vendas-combustiveis-m3.xlsx'

# loading excel file sales fuel by UF and product
df_fuel = pd.read_excel(filename, sheet_name='DPCache_m3')

# loading excel file sales of diesel by UF and type
df_diesel = pd.read_excel(filename, sheet_name='DPCache_m3 -1')

# Manipulating dataframes
df_stg_fuel = pd.DataFrame(df_fuel)
df_stg_diesel = pd.DataFrame(df_diesel)

# Rename columns in dataframe 
df_stg_fuel.rename(columns={'COMBUSTÍVEL': 'combustivel', 'ANO': 'ano', 'REGIÃO': 'regiao', 'ESTADO':'estado',
                            'UNIDADE':'unidade','Jan':'jan','Fev':'fev','Mar':'mar','Abr':'abr','Mai':'mai',
                            'Jun':'jun','Jul':'jul','Ago':'ago','Set':'set', 'Out':'out','Nov':'nov'
                            , 'Dez':'dez', 'TOTAL':'total'}, inplace=True)

df_stg_diesel.rename(columns={'COMBUSTÍVEL': 'combustivel', 'ANO': 'ano', 'REGIÃO': 'regiao', 'ESTADO':'estado',
                            'UNIDADE':'unidade','Jan':'jan','Fev':'fev','Mar':'mar','Abr':'abr','Mai':'mai',
                            'Jun':'jun','Jul':'jul','Ago':'ago','Set':'set', 'Out':'out','Nov':'nov'
                            , 'Dez':'dez', 'TOTAL':'total'}, inplace=True)


# List UF from brazilian states
uf_list = {'RONDÔNIA':'RO', 'ACRE':'AC', 'AMAZONAS':'AM', 'RORAIMA':'RR', 'PARÁ':'PA', 'AMAPÁ':'AP',
           'TOCANTINS':'TO', 'MARANHÃO':'MA', 'PIAUÍ':'PI', 'CEARÁ':'CE', 'RIO GRANDE DO NORTE':'RN',
           'PARAÍBA':'PB', 'PERNAMBUCO':'PE', 'ALAGOAS':'AL', 'SERGIPE':'SE', 'BAHIA':'BA',
           'MINAS GERAIS':'MG', 'ESPÍRITO SANTO':'ES', 'RIO DE JANEIRO':'RJ', 'SÃO PAULO':'SP',
           'PARANÁ':'PR', 'SANTA CATARINA':'SC', 'RIO GRANDE DO SUL':'RS','MATO GROSSO DO SUL':'MS', 
           'MATO GROSSO':'MT', 'GOIÁS':'GO', 'DISTRITO FEDERAL':'DF'}

# Adding new column UF from brazilian states
df_stg_fuel['uf'] = df_stg_fuel.estado.map(uf_list)
df_stg_diesel['uf'] = df_stg_diesel.estado.map(uf_list)         

# Removing m3 from string combustivel to add product column
df_stg_fuel['produto'] = df_stg_fuel['combustivel'].apply(lambda x: x.split("(m3)")[0])
df_stg_diesel['produto'] = df_stg_diesel['combustivel'].apply(lambda x: x.split("(m3)")[0])

# Preparing columns to Unpivot
df_stg_fuel = df_stg_fuel.drop(columns=['combustivel','total'])
df_stg_diesel = df_stg_diesel.drop(columns=['combustivel','total'])

# Unpivot data from column to lines
df_stg_fuel_melt = pd.melt(
    df_stg_fuel,
    id_vars = ['produto','unidade','regiao','estado','uf','ano'],
    var_name = 'mes',
    value_name='volume'
)

df_stg_diesel_melt = pd.melt(
    df_stg_diesel,
    id_vars = ['produto','unidade','regiao','estado','uf','ano'],
    var_name = 'mes',
    value_name='volume'
)

# Adding number to months from string names
month_list = {'jan':1, 'fev':2, 'mar':3, 'abr':4, 'mai':5, 'jun':6,'jul':7,'ago':8, 'set':9,'out':10, 'nov':11, 'dez':12}

df_stg_fuel_melt['month'] = df_stg_fuel_melt.mes.map(month_list)
df_stg_diesel_melt['month'] = df_stg_diesel_melt.mes.map(month_list)

# Replace NAN and Null values with 0
df_stg_fuel_melt['volume'].fillna(0, inplace=True)
df_stg_diesel_melt['volume'].fillna(0, inplace=True)

# creating column date 
df_stg_fuel_melt['year_month'] = pd.to_datetime(df_stg_fuel_melt.ano.astype(str) + '/' + df_stg_fuel_melt.month.astype(str) + '/01')
df_stg_diesel_melt['year_month'] = pd.to_datetime(df_stg_diesel.ano.astype(str) + '/' + df_stg_diesel_melt.month.astype(str) + '/01')

# Process to Write the data
df_refined_fuel = pd.DataFrame(df_stg_fuel_melt[['year_month','estado','produto','unidade','volume']])
df_refined_diesel = pd.DataFrame(df_stg_diesel_melt[['year_month','estado','produto','unidade','volume']])

# Renaming columns
df_refined_fuel.rename(columns={'year_month':'year_month','estado':'uf','produto': 'product','unidade':'unit',  
                                'volume':'volume'}, inplace=True)

df_refined_diesel.rename(columns={'year_month':'year_month','estado':'uf','produto': 'product','unidade':'unit',  
                                  'volume':'volume'}, inplace=True)                                

# Timestamp column
df_refined_fuel['created_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
df_refined_diesel['created_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')   

print("-----------------------------------------")
print("Total lines from Fuel dataframe: ",df_refined_fuel.shape)
print("")
print("")
print("-----------------------------------------")
print("Total lines from Diesel dataframe: ", df_refined_diesel.shape)

# Process to write to SQL Lite
# Remove file with database SQLLite (if exists)
os.remove(cwd + "/data/anp.db") if os.path.exists(cwd + "/data/anp.db") else None

# Connection with database SQL Lite
con = sqlite3.connect(cwd + "/data/anp.db")

# Create Cursor 
cur = con.cursor()

# Create table Fuel with sql
sql_create_fuel = 'CREATE TABLE IF NOT EXISTS refined_tb_oil_derivative '\
'(id integer PRIMARY KEY AUTOINCREMENT NOT NULL, '\
'year_month  DATE, '\
'uf          VARCHAR(100), '\
'product     VARCHAR(100), '\
'unit        VARCHAR(10), '\
'volume      REAL, '\
'created_at  TIMESTAMP)'

# Create table Diesel with sql
sql_create_diesel = 'CREATE TABLE IF NOT EXISTS refined_tb_diesel '\
'(id integer PRIMARY KEY AUTOINCREMENT NOT NULL, '\
'year_month  DATE, '\
'uf          VARCHAR(100), '\
'product     VARCHAR(100), '\
'unit        VARCHAR(10), '\
'volume      REAL, '\
'created_at  TIMESTAMP)'

cur.execute(sql_create_fuel)
print('Table Fuel created')

cur.execute(sql_create_diesel)
print('Table Diesel created')

# Insert values from dataframe to refined
df_refined_fuel.to_sql('refined_tb_oil_derivative', con=con, if_exists="append", index=False)

# Insert values from dataframe to refined
df_refined_diesel.to_sql('refined_tb_diesel', con=con, if_exists="append", index=False)

# Selecting total from oil derivative 
sql_fuel_count = 'SELECT count(*) total FROM refined_tb_oil_derivative'
cur.execute(sql_fuel_count)
dados_fuel = cur.fetchall()

# Selecting total from oil derivative 
sql_diesel_count = 'SELECT count(*) total FROM refined_tb_diesel'
cur.execute(sql_diesel_count)
dados_diesel = cur.fetchall()

print("Total lines from dataframes write in oil derivative : ", dados_fuel)
print("")
print("")
print("-----------------------------------------")
print("Total lines from dataframes write in oil derivative : ", dados_diesel)
print("")
print("")
print("-----------------------------------------")
print("Total Derivados combustíveis de petróleo e UF")

# format numeric values
pd.options.display.float_format = '{:,.0f}'.format

# Total from fuel derivates
group_fuel = df_stg_fuel_melt.groupby('ano')
resultado_fuel = group_fuel["volume"].sum()
print("Total volume 'Fuel': ", resultado_fuel.head(21))


print("")
print("")
print("-----------------------------------------")
print("Total de óleo diesel e UF")
# Total from oleo diesel
group_diesel = df_stg_diesel_melt.groupby('ano')
resultado_diesel = group_diesel["volume"].sum()
print("Total volume 'Diesel': ", resultado_diesel.head(12))

# Close connection with database
con.close()
