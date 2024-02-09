# -*- coding: utf-8 -*-
"""
@author: nicolasledurf
"""

import requests as rq
import pandas as pd
import ssl
import io

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
#Função para transformar o formato da data que para qual eu prefiro
def textoParaData(valor):
  return valor[:-2] + '-' + valor[-2:] + '-01'

#Função para transformar valores indexadores em variação acumulada em 12 meses
def index12m(dataframe):
    df = dataframe.copy()
    df['data'] = pd.to_datetime(df['data'], format='%Y--%m-%d')
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
    data['data'] = pd.to_datetime(data['data'], format='%Y--%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    data = data[['data', 'variacao']]
    data = data.rename(columns={'variacao': 'valor'})

    data = data.dropna(subset=['valor'], inplace=False)
    return data

#Função para extrair dados do ECB como indexadores
def extractECBIndex(resource, flowRef, key, parameters):
    with rq.session() as s:
       s.mount("https://", TLSAdapter())
       wsEntryPoint = "https://data-api.ecb.europa.eu/"    
       data = rq.get(wsEntryPoint + resource + flowRef + key + "?" + parameters)   
       data = data.text 
       
       df = pd.read_csv(io.StringIO(data))
       
       df = df[["TIME_PERIOD", "OBS_VALUE"]]
       df["data"] = df["TIME_PERIOD"].apply(textoParaData)
       df = df.rename(columns={'OBS_VALUE': 'valor'})
       df = df[['data', 'valor']]
       #df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
       return df
   
#Função para extrair dados do ECB como taxas/percentagem
def extractECBrates(resource, flowRef, key, parameters):
    with rq.session() as s:
       s.mount("https://", TLSAdapter())
       wsEntryPoint = "https://data-api.ecb.europa.eu/"    
       data = rq.get(wsEntryPoint + resource + flowRef + key + "?" + parameters)   
       data = data.text 
     
       df = pd.read_csv(io.StringIO(data))
       
       df = df[["TIME_PERIOD", "OBS_VALUE"]]
       #df["data"] = df["TIME_PERIOD"].apply(mesForData)
       df = df.rename(columns={'OBS_VALUE': 'valor', "TIME_PERIOD": "data"})
       df = df[['data', 'valor']]
       return df
   
    
#Função para extrair dados do ECB como valores brutos
def extractECvalues(resource, flowRef, key, parameters):
    with rq.session() as s:
       s.mount("https://", TLSAdapter())
       wsEntryPoint = "https://data-api.ecb.europa.eu/"    
       data = rq.get(wsEntryPoint + resource + flowRef + key + "?" + parameters)   
       data = data.text 
       
       df = pd.read_csv(io.StringIO(data))
      
       df = df[["TIME_PERIOD", "OBS_VALUE"]]
       df["data"] = df["TIME_PERIOD"].apply(textoParaData)
       df = df.rename(columns={'OBS_VALUE': 'valor'})
       df = df[['data', 'valor']]
       return df    

"""
Extração de dados
"""
#agregados monetários/europa
#Agregado M1 na Europa
m1Europa = extractECvalues("service/data/", "BSI/", "M.U2.Y.V.M10.X.1.U2.2300.Z01.E", "format=csvdata&startPeriod=2000-01-01")
    
#Agregado M2 na Europa
m2Europa = extractECvalues("service/data/", "BSI/", "M.U2.Y.V.M20.X.1.U2.2300.Z01.E", "format=csvdata&startPeriod=2000-01-01")
    
#Agregado M3 na Europa
m3Europa = extractECvalues("service/data/", "BSI/", "M.U2.Y.V.M30.X.1.U2.2300.Z01.E", "format=csvdata&startPeriod=2000-01-01")

#juros/europa
#Juros de Depósito definido BCE
jurosDepositosEU = extractECBrates("service/data/", "FM/", "B.U2.EUR.4F.KR.DFR.LEV", "format=csvdata&startPeriod=2000-01-01")
    
#Juros de Refinanciamento definido pelo BCE
jurosRefEU = extractECBrates("service/data/", "FM/", "B.U2.EUR.4F.KR.MRR_FR.LEV", "format=csvdata&startPeriod=2000-01-01")
    
#Juros de Facilidade de Empréstimos Marginal definido pelo BCE
jurosFacilidadeEU = extractECBrates("service/data/", "FM/", "B.U2.EUR.4F.KR.MLFR.LEV", "format=csvdata&startPeriod=2000-01-01")

#PPI/EURO
#Variação Mensal do PPI na Europa
index = extractECBIndex("service/data/", "STS/", "M.I9.N.PRON.2C0000.4.000", "format=csvdata&startPeriod=2000-01-01")
ppiEuropaMensal = indexMensal(index)
del index

#Variação Acumulada no Ano do PPI na Europa
index = extractECBIndex("service/data/", "STS/", "M.I9.N.PRON.2C0000.4.000", "format=csvdata&startPeriod=2000-01-01")
mensal = indexMensal(index)
ppiEuropaAnual = indexAnual(mensal)
del index, mensal

#Variação Acumulada em 12 meses do PPI na Europa
index = extractECBIndex("service/data/", "STS/", "M.I9.N.PRON.2C0000.4.000", "format=csvdata&startPeriod=2000-01-01")
ppiEuropa12m = index12m(index)
del index

#Produção Industrial/EURO
#Variação Mensal da Produção Industrial na Europa
index = extractECBIndex("service/data/", "STS/", "M.I9.W.PROD.NS0020.4.000", "format=csvdata&startPeriod=2000-01-01")
piEuropaMensal = indexMensal(index)
del index

#Variação Acumulada no Ano da Produção Industrial na Europa
index = extractECBIndex("service/data/", "STS/", "M.I9.W.PROD.NS0020.4.000", "format=csvdata&startPeriod=2000-01-01")
mensal = indexMensal(index)
piEuropaAnual = indexAnual(mensal)
del index, mensal

#Variação Acumulada em 12 meses da Produção Industrial na Europa
index = extractECBIndex("service/data/", "STS/", "M.I9.W.PROD.NS0020.4.000", "format=csvdata&startPeriod=2000-01-01")
piEuropa12m = index12m(index)
del index

#Inflação/EURO
#Variação Mensal do CPI na Europa
inflationIndex = extractECBIndex("service/data/", "ICP/", "M.U2.N.000000.4.INX", "format=csvdata&startPeriod=2000-01-01")
cpiEuroMensal = indexMensal(inflationIndex)
del inflationIndex

#Variação Acumulada no Ano do CPI na Europa
inflationIndex = extractECBIndex("service/data/", "ICP/", "M.U2.N.000000.4.INX", "format=csvdata&startPeriod=2000-01-01")
mensal = indexMensal(inflationIndex)
cpiEuroAnual = indexAnual(mensal)
del inflationIndex, mensal

#Variação Acumulada em 12 meses do CPI na Europa
inflationIndex = extractECBIndex("service/data/", "ICP/", "M.U2.N.000000.4.INX", "format=csvdata&startPeriod=2000-01-01")
cpiEuro12M = index12m(inflationIndex)
del inflationIndex

#Nucleo da Inflação/EURO
#Variação Mensal do Núcleo do CPI na Europa
inflationIndex = extractECBIndex("service/data/", "ICP/", "M.U2.N.XEF000.4.INX", "format=csvdata&startPeriod=2000-01-01")
ncpiEuroMensal = indexMensal(inflationIndex)
del inflationIndex

#Variação Acumulada no Ano do Núcleo do CPI na Europa
inflationIndex = extractECBIndex("service/data/", "ICP/", "M.U2.N.XEF000.4.INX", "format=csvdata&startPeriod=2000-01-01")
mensal = indexMensal(inflationIndex)
ncpiEuroAnual = indexAnual(mensal)
del inflationIndex, mensal

#Variação Acumulada em 12 meses do Núcleo do CPI na Europa
inflationIndex = extractECBIndex("service/data/", "ICP/", "M.U2.N.XEF000.4.INX", "format=csvdata&startPeriod=2000-01-01")
ncpiEuro12M = index12m(inflationIndex)
del inflationIndex
