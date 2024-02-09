# -*- coding: utf-8 -*-
"""
@author: nicolasledurf
"""
import requests as rq
import pandas as pd
import ssl
import dbnomics as db

#Função para garantir que as requisições funcionem 
#independentemente das questões de segurança do site
class TLSAdapter(rq.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.options |= 0x4
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
    
"""
Funções de Extração e Tratamento de Dados
"""

#Função para obter os dados em indexador/valor do DBnomics
def indexDBnomics(sufix, serie, espec):
    df = db.fetch_series(sufix, serie, espec)
    df = df[['period', "value"]]

    df = df.rename(columns={'period': 'data', 'value': 'valor'})
    df = df.dropna(subset=['valor'], inplace=False)
    df['data'] = df['data'].apply(lambda x: x.strftime('%Y-%m-%d'))
    return df

#Função para transformar os dados extraídos do DBnomics em variação acumulada em 12 meses
def index12mDBnomics(data):
    df = data.copy()
    
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df['12meses'] = df['valor'].pct_change(periods=12) * 100
    df['12meses'] = df['12meses'].round(2)
    df = df.drop(columns=['valor'])
    df = df.rename(columns={'12meses': 'valor'})
    df = df.dropna(subset=['valor'], inplace=False)
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    
    return df

#Função para transformar os dados extraídos do DBnomics em varição acumulada no ano
def indexAnualDBnomics(data):
    df = data.copy()
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')

    dfdatas = df.copy()
    dfdatas = dfdatas[['data']]
    
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df['ano'] = df['data'].dt.year
    df = df[['ano', 'valor']]
    df['anual'] = df.groupby(['ano'])['valor'].transform(lambda x: ((1 + x / 100).cumprod() - 1) * 100)
    
    df = pd.merge(df, dfdatas, left_index=True, right_index=True)
    
    df = df.drop(columns=['valor', 'ano'])
    df = df.rename(columns={'anual': 'valor'})
    df['valor'] = df['valor'].round(2)
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    return df

#Função para transformar os dados extraídos do DBnomics em varição mensal
def indexMensalDBnomics(df): 
    data = df.copy()
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d')
    data = data.sort_values(by='data')
    data['variacao'] = ((data['valor'] - data['valor'].shift(1)) / data['valor'].shift(1)) * 100
    
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    data = data[['data', 'variacao']]
    data = data.rename(columns={'variacao': 'valor'})
    data = data.dropna(subset=['valor'], inplace=False)
    data['valor'] = data['valor'].round(2)

    return data

"""
Extração de Dados
"""
#PIB em Variação Mensal/China
pibMensalChina = indexDBnomics("NBS", "Q_A0104", "A010401")

#Agregados Monetários/China
#M0 na China em 100 milhões de yuan
m0China = indexDBnomics("NBS", "M_A0D01", "A0D0105")

#M1 na China em 100 milhões de yuan
m1China = indexDBnomics("NBS", "M_A0D01", "A0D0103")

#M2 na China em 100 milhões de yuan
m2China = indexDBnomics("NBS", "M_A0D01", "A0D0101")
    
#Taxa de Desemprego na China em Percentagem
desempregoChina = indexDBnomics("NBS", "M_A0E01", "A0E0101")
    
#Exportações e Importações/China
#Exportações Totais Correntes da China em mil dólares
exportCorrenteChina = indexDBnomics("NBS", "M_A0801", "A080109")

#Exportações Totais Acumuladas da China em mil dólares
exportAcumChina = indexDBnomics("NBS", "M_A0801", "A080107")

#Importações Totais Correntes da China em mil dólares
importCorrenteChina = indexDBnomics("NBS", "M_A0801", "A080105")

#Importações Totais Acumuladas da China em mil dólares
importAcumChina = indexDBnomics("NBS", "M_A0801", "A08010B")

#Vendas no Varejo de Bens de Consumo/China
dvendasVarejoChinaIndex = indexDBnomics("NBS", "M_A0701", "A070101")

#Variação Mensal das Vendas no Varejo de Bens de Consumo 
i = indexDBnomics("NBS", "M_A0701", "A070101")
vendasVarejoChinaMensal = indexMensalDBnomics(i)
del i

#Variação Acumulada no Ano das Vendas no Varejo de Bens de Consumo
i = indexDBnomics("NBS", "M_A0701", "A070101")
m = indexMensalDBnomics(i)
vendasVarejoChinaAnual = indexAnualDBnomics(m)

#Compras de Gerentes de Manufatura/China
cgmChinaIndex = indexDBnomics("NBS", "M_A0B01", "A0B0101")

#Variação Mensal de Compras de Gerentes de Manufatura
i = indexDBnomics("NBS", "M_A0B01", "A0B0101")
cgmChinaMensal = indexMensalDBnomics(i)
del i

#Variação Acumulada no Ano de Compras de Gerentes de Manufatura
i = indexDBnomics("NBS", "M_A0B01", "A0B0101")
m = indexMensalDBnomics(i)
cgmChinaAnual = indexAnualDBnomics(m)
del i, m

#Variação Acumulada em 12 meses de Compras de Gerentes de Manufatura
i = indexDBnomics("NBS", "M_A0B01", "A0B0101")
cgmChina12m = index12mDBnomics(i)
del i

#Produção Industrial/China
prodIndChinaIndex = indexDBnomics("NBS", "M_A0B01", "A0B0102", )
    
#PMI da Produção Industrial na Variação Mensal
i = indexDBnomics("NBS", "M_A0B01", "A0B0102")
prodIndChinaMensal = indexMensalDBnomics(i)
del i

#PMI da Produção Industrial na Variação Acumulada no Ano
i = indexDBnomics("NBS", "M_A0B01", "A0B0102")
m = indexMensalDBnomics(i)
prodIndChinaAnual = indexAnualDBnomics(m)
del i, m
    
#PMI da Produção Industrial na Variação Acumulada em 12 meses
i = indexDBnomics("NBS", "M_A0B01", "A0B0102")
prodIndChina12m = index12mDBnomics(i)    
del i

#PPI/China
#Variação Mensal do PPI
i = indexDBnomics("NBS", "M_A010807", "A01080701")
ppiChinaMensal = indexMensalDBnomics(i)
del i

#Variação Acumulada no Ano do PPI
i = indexDBnomics("NBS", "M_A010807", "A01080701")
m = indexMensalDBnomics(i)
ppiChinaAnual = indexAnualDBnomics(m)
del i, m

#Variação Acumulada em 12 meses do PPI
i = indexDBnomics("NBS", "M_A010807", "A01080701")
ppiChina12m = index12mDBnomics(i)
del i

#CPI/China
#Variação Mensal do CPI
i = indexDBnomics("NBS", "M_A010301", "A01030101")
cpiChinaMensal = indexMensalDBnomics(i)
del i

#Variação Acumulada no ano do CPI
i = indexDBnomics("NBS", "M_A010301", "A01030101")
m = indexMensalDBnomics(i)
cpiChinaAnual = indexAnualDBnomics(m)
del i, m

#Variação Acumulada em 12 meses do CPI
i = indexDBnomics("NBS", "M_A010301", "A01030101")
cpiChina12m = index12mDBnomics(i)
del i
