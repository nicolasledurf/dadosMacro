# -*- coding: utf-8 -*-
"""
@author: nicolasledurf
"""

import requests as rq
import pandas as pd
import os
import ssl

api_key = os.environ.get('APIKEY_FED')

"""
Funções auxiliares
"""    
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
Funções de tratamento e extração de dados
"""
#Função para transformar valores indexadores em variação acumulada em 12 meses
def index12m(dataframe):
    df = dataframe.copy()
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df['12meses'] = df['valor'].pct_change(periods=12) * 100
    df['12meses'] = df['12meses'].round(2)
    df = df.drop(columns=['valor'])
    df = df.rename(columns={'12meses': 'valor'})
    df = df.dropna(subset=['valor'], inplace=False)
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))

    return df

#Função para transformar valores indexadores em variação acumulada anual
def indexAnual(dataframe):
    df = dataframe.copy()
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

#Função para transformar valores indexadores em variação mensal
def indexMensal(dataframe): 
    data = dataframe.copy()
    data = data.sort_values(by='data')
    
    data['variacao'] = ((data['valor'] - data['valor'].shift(1)) / data['valor'].shift(1)) * 100
    
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    data = data[['data', 'variacao']]
    data = data.rename(columns={'variacao': 'valor'})

    data = data.dropna(subset=['valor'], inplace=False)
    return data

#Função para calcular a variação do GDP Acumulado no Ano
def GDPAnual(dataframe):
    dfanual = dataframe.copy()
    dfanual['ano'] = dfanual['data'].dt.year
    dfanual['trimestre'] = dfanual['valor'].astype(float)
    dfdatas = dfanual.copy()
    dfdatas = dfdatas[['data']]
    dfanual = dfanual[['ano', 'trimestre']]
    dfanual['anual'] = dfanual.groupby(['ano'])['trimestre'].transform(lambda x: ((1 + x / 100).cumprod() - 1) * 100)
    dfanual['anual'] = dfanual['anual'].round(2)
    dfanual = pd.merge(dfanual, dfdatas, left_index=True, right_index=True)
    dfanual = dfanual.rename(columns={'anual': 'valor'})
    dfanual = dfanual[['data', 'valor']]
    dfanual = dfanual.dropna(subset=['valor'], inplace=False)
    dfanual['data'] = pd.to_datetime(dfanual['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    return dfanual

#Função para calcular a variação do GDP Acumulado em 4 Trimestres
def GDP4Trim(dataframe):
    df = dataframe.copy()
    df['data'] = pd.to_datetime(df['data'])
    df['média móvel'] = df['valor'].rolling(window=4).mean()
    df['4trimestres'] = df['valor'].pct_change(periods=4) * 100
    df = df.drop(columns=['valor'])
    df = df.rename(columns={'4trimestres': 'valor'})
    df = df[['data', 'valor']]
    df = df.dropna(subset=['valor'], inplace=False)
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    return df

#Função para calcular a variação do GDP por trimestre
def GDPTrim(dataframe):
    df = dataframe.copy()
    df['data'] = pd.to_datetime(df['data'])
    df['média móvel'] = df['valor'].rolling(window=4).mean()
    df['trimestre'] = df['valor'].pct_change() * 100
    df = df.drop(columns=['valor'])
    df = df.rename(columns={'trimestre': 'valor'})
    df = df[['data', 'valor']]
    df = df.dropna(subset=['valor'], inplace=False)
    #df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    return df
    

#Função para extrair e tratar os dados exclusivamente do payroll
def tratFEDpayroll(serie):
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={serie}&api_key={api_key}&file_type=json'

    # Obtenha os dados da API do FRED
    response = rq.get(url)

    datajson = response.json()
    datareleases = datajson['observations']

    data = pd.DataFrame(datareleases)
    data = data[['date', 'value']]
    data = data.rename(columns={'date': 'data', 'value': 'valor'})
    
    data['valor'] = data['valor'].astype(float)
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d')
    
    data.set_index('data', inplace=True)
    data['diferenca'] = data['valor'].diff()
    data.reset_index(inplace=True)
    
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    
    data = data.drop(columns=['valor'])
    data = data.rename(columns={'diferenca': 'valor'})
    data['valor'] = data['valor'] * 1000
    
    return data
        
#Função para tratar os dados obtidos via FED que retornam os valores
#em indexador. 
def tratFEDIndex(serie):
    url = f'https://api.stlouisfed.org/fred/series/observations?series_id={serie}&api_key={api_key}&file_type=json'
    
    response = rq.get(url)
    datajson = response.json()
    datareleases = datajson['observations']

    data = pd.DataFrame(datareleases)
    data = data[['date', 'value']]
    data = data.rename(columns={'date': 'data', 'value': 'valor'})
    data = data[data['valor'] != '.']
    
    data['valor'] = data['valor'].astype(float)
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d')
    data = data[['data', 'valor']]

    data = data.sort_values(by='data')
    return data

"""
Extração e tratamento dos dados
"""
#Meio Monetário M1/EUA
m1EUA = tratFEDIndex('M1REAL')   
    
#Meio Monetário M2/EUA
m2EUA = tratFEDIndex('M2REAL')   
    
#pedidos de bens duráveis/EUA
ordersDurableGoods = tratFEDIndex('ADXTNO')   
    
#Expectativa de Inflação/EUA
expectInflacaoEUA = tratFEDIndex('MICH')   
    
#payroll/EUA
payrollEUA = tratFEDpayroll('PAYEMS')
    
#GDP (Gross Domestic Product) em Valor Bruto em bilhões de dólares
gdpBruto = tratFEDIndex('GDP')

#GDP (Gross Domestic Product) na variação do trimestre comparado
#ao trimestre imediatamente anterior
gdp = tratFEDIndex('GDP')
GDPTrimEUA = GDPTrim(gdp)
del gdp

#GDP (Gross Domestic Product) na variação acumulada em 4 trimestres
gdp = tratFEDIndex('GDP')
GDP4TrimEUA = GDP4Trim(gdp)
del gdp

#GDP (Gross Domestic Product) na variação acumulada no ano
gdpvar = tratFEDIndex('GDP')
gdp = GDPTrim(gdpvar)
GDPAnualEUA = GDPAnual(gdp)

del gdpvar, gdp

#Juros Hipoteca de 30 anos
jurosHipoteca30anos = tratFEDIndex('MORTGAGE30US')
    
#Ganho Médio por Hora Trabalhada, Total Privado, na Variação Mensal
ganhoMedio = tratFEDIndex('CES0500000003')
ganhoMedioEUA = indexMensal(ganhoMedio)
del ganhoMedio    

#Ganho Médio por Hora Trabalhada, Total Privado, na Variação Acumulada no Ano
ganhoMedio = tratFEDIndex('CES0500000003')
ganhoMensalMedio = indexMensal(ganhoMedio)
ganhoMedioAnualEUA = indexAnual(ganhoMensalMedio)
    
del ganhoMedio, ganhoMensalMedio

#CPI/EUA
#Variação Mensal do CPI
df = tratFEDIndex('CPIAUCSL')
CPIMensalEUA = indexMensal(df)
del df

#Variação Acumulada no ano do CPI
df = tratFEDIndex('CPIAUCSL')
dfmensal = indexMensal(df)
CPIAnualEUA = indexAnual(dfmensal)
del df, dfmensal

#Variação Acumulada em 12 meses do CPI
df = tratFEDIndex('CPIAUCSL')
CPI12mEUA = index12m(df)
del df
    
#Variação Mensal do Núcleo do CPI
df = tratFEDIndex('CPILFESL')
nCPIMensalEUA = indexMensal(df)
del df
    
#Variação Acumulada no Ano do Núcleo do CPI
df = tratFEDIndex('CPILFESL')
dfmensal = indexMensal(df)
nCPIAnualEUA = indexAnual(dfmensal)
del df, dfmensal

#Variação Acumulada em 12 meses do Núcleo do CPI
df = tratFEDIndex('CPILFESL')
nCPI12mEUA = index12m(df)
del df
    
#Variação Mensal do Personal Consumption Expenditures (PCE)
df = tratFEDIndex('PCEPI')
PCEMensalEUA = indexAnual(df)
del df
    
#Variação Acumulada no ano do Personal Consumption Expenditures (PCE)
df = tratFEDIndex('PCEPI')
dfmensal = indexMensal(df)
PCEAnualEUA = indexAnual(dfmensal)
del df, dfmensal

#Variação Acumulada em 12 meses do Personal Consumption Expenditures (PCE)
df = tratFEDIndex('PCEPI')
PCE12mEUA = index12m(df)
del df
    
#Núcleo do PCE na variação Mensal
df = tratFEDIndex('PCEPILFE')
nPCEMensalEUA = indexMensal(df)
del df
    
#Núcleo do PCE na variação acumulada no ano
df = tratFEDIndex('PCEPILFE')
dfmensal = indexMensal(df)
nPCEAnualEUA = indexAnual(dfmensal)
del df, dfmensal

#Núcleo do PCE na variação acumulada em 12 meses
df = tratFEDIndex('PCEPILFE')
nPCE12mEUA = index12m(df)
del df
    
#Produção Industrial: Index Total na variação mensal
df = tratFEDIndex('INDPRO')
PIMensalEUA = indexMensal(df)
del df
    
#Produção Industrial: Index Total na variação acumulada no ano
df = tratFEDIndex('INDPRO')
dfmensal = indexMensal(df)
PIAnualEUA = indexAnual(dfmensal)
del df, dfmensal

#Produção Industrial: Index Total na variação acumulada em 12 meses
df = tratFEDIndex('INDPRO')
PI12mEUA = index12m(df)
del df
    
#Variação Mensal do Producer Price Index by Commodity, Final Demanda
df = tratFEDIndex('PPIFIS')
PPIMensalEUA = indexMensal(df)
del df

#Variação Acumulada no Ano do Producer Price Index by Commodity, Final Demanda
df = tratFEDIndex('PPIFIS')
dfmensal = indexMensal(df)
PPIAnualEUA = indexAnual(dfmensal)
del df, dfmensal

#Variação Acumulada em 12 meses do Producer Price Index by Commodity, Final Demanda
df = tratFEDIndex('PPIFIS')
PPI12mEUA = index12m(df)
del df
    
#Vendas no Varejo na variação mensal
df = tratFEDIndex('RSXFS')
VVMensalEUA = indexMensal(df)
del df

#Vendas no Varejo na variação acumulada no ano
df = tratFEDIndex('RSXFS')
dfmensal = indexMensal(df)
VVAnualEUA = indexAnual(dfmensal)
del df, dfmensal

#Vendas no Varejo na variação acumulada em 12 meses
df = tratFEDIndex('RSXFS')
VV12mEUA = index12m(df)
del df

#Pedidos iniciais por Seguro Desemprego em pessoas
initialClaims = tratFEDIndex('ICSA')

#FFR - Taxa Básica de juros Americana, limite máximo/EUA
FFRmax = tratFEDIndex('DFEDTARU')

#FFR - Taxa Básica de juros Americana, limite mínimo/EUA
FFRmin = tratFEDIndex('DFEDTARL')
    
#Treasuries/EUA
#Títulos do Tesouro Americano com vencimento em 5 anos, indexados pela inflação
treasuries5 = tratFEDIndex('DGS5')

#Títulos do Tesouro Americano com vencimento em 10 anos, indexados pela inflação
treasuries10 = tratFEDIndex('DGS10')

#Títulos do Tesouro Americano com vencimento em 20 anos, indexados pela inflação
treasuries20 = tratFEDIndex('DGS20')

#Variação de novos peiddos para manufatura: bens duráveis excento transporte
ordersDurableGoods = tratFEDIndex('ADXTNO')   

#Expectativa de Inflação/EUA
expectInflacaoEUA = tratFEDIndex('MICH')   