# -*- coding: utf-8 -*-
"""
@author: nicolasledurf
"""
import requests as rq
import ssl
import ipeadatapy as idpy
import pandas as pd

"""
Funções
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
    
    
#Função para obter a variação mensal dos dados
def varMensal(dataframe): 
    data = dataframe.copy()
    data = data.sort_values(by='data')
    
    data['variacao'] = ((data['valor'] - data['valor'].shift(1)) / data['valor'].shift(1)) * 100
    
    data['data'] = pd.to_datetime(data['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    data = data[['data', 'variacao']]
    data = data.rename(columns={'variacao': 'valor'})

    data = data.dropna(subset=['valor'], inplace=False)
    return data

    
#Função para calcular o acumulado em 12 meses dos dados obtidos no Ipeadata
def dozemeses(df):
    df['12meses'] = df['valor'].rolling(window=12).apply(lambda x: ((1 + x / 100).prod() - 1) * 100, raw=True)
    df['12meses'] = df['12meses'].round(2)
    df = df.drop(columns=['valor'])
    df = df.rename(columns={'12meses': 'valor'})
    
    df['data'] = df['data'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df.dropna(subset=['valor'], inplace=True)
    return df

#Função para calcular o acumulado no ano dos dados obtidos no Ipeadata
def anual(df):
    df['ano'] = df['data'].dt.year
    
    df['anual'] = df.groupby(['ano'])['valor'].apply(lambda x: ((1 + x / 100).cumprod() - 1) * 100).reset_index()
    df['anual'] = df['anual'].round(2)
    
    df = df.drop(columns=['valor', 'ano'])
    df = df.rename(columns={'anual': 'valor'})
    
    df['data'] = df['data'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df.dropna(subset=['valor'], inplace=True)
    return df

#Função para extrair e tratar dados originados do Ipeadata e retornar a data
#como string
def ipeadataValor(serie, columnName):
    data = idpy.timeseries(serie)
    data = data.astype(str)
    data = data.drop(
            data.columns[[0, 1, 2, 3]], axis=1).reset_index()

    data = data.rename(columns={'DATE': 'data', columnName: 'valor'})
    data['valor'] = data['valor'].astype(float)
    data = data.dropna(subset=['valor'])
    
    data['data'] = data['data'].apply(lambda x: x.strftime('%Y-%m-%d'))
    data = data[['data', 'valor']]
    return data

#Função para extrair e dados orginados do Ipeadata e retornar a 
#data como datetime
def ipeadataMensal(serie, columnName):
    data = idpy.timeseries(serie)
    data = data.astype(str)
    data = data.drop(
            data.columns[[0, 1, 2, 3]], axis=1).reset_index()

    data = data.rename(columns={'DATE': 'data', columnName: 'valor'})
    data['valor'] = data['valor'].astype(float)

    data = data[['data', 'valor']]
    return data

"""
Extração dos dados
"""
#SELIC
selic = ipeadataValor('BM366_TJOVER366', 'VALUE ((% a.a.))')
    
#Operações de Crédito, Saldo da Carteira, Recursos Livres Total
#na Variação Mensal/Brasil
i = ipeadataMensal("BM12_CRLS12", 'VALUE (R$)')
operacoesCreditoMensalBR = varMensal(i)
del i

#Operações de Crédito, Saldo da Carteira Total
#na Variação Mensal/Brasil
i = ipeadataMensal("BM12_CS12", 'VALUE (R$)')
operacoesCreditoTotalMensalBR = varMensal(i)
del i

#IBC-Br Índice Real Dessazonalizado (2002=100) na Variação Mensal em %
i = ipeadataMensal("SGS12_IBCBRDESSAZ12", 'VALUE (-)')
IBCBrMensal = varMensal(i)
del i

#Meios de Pagamento/Brasil
#M0: papel-moeda emitido em milhões de reais
meio0BR = ipeadataValor('BM12_PME12', 'VALUE (R$)')

#M1: Depósitos à Vista + PMPP em milhões de reais
meio1BR = ipeadataValor('BM12_M1N12', 'VALUE (R$)')

#M2: M1 + Poupança + Títulos Privados em milhões de reais
meio2BR = ipeadataValor('BM12_M2NCN12', 'VALUE (R$)')

#M3: M2 + Cotas de Fundos + Operações Comprom. de Títulos Públicos e Federais
#em milhões de reais
meio3BR = ipeadataValor('BM12_M3NCN12', 'VALUE (R$)')

#M4: M3 + Títulos emitidos pelo Governo Federal em milhões de reais
meio4BR = ipeadataValor('BM12_M4NCN12', 'VALUE (R$)')
    
#NTN/Brasil
#Dívida Interna Federal, fora do BC, posição em carteira, fim de período, 
#em milhões de reais
ntn = ipeadataValor('BM12_DIVFBC12', 'VALUE (R$)')
    
#NFSP/Brasil
#Necessidade de Financiamento do Setor Público Acum. em 12 meses em 
#milhões de reais
nfsp = ipeadataValor('BM12_NFSPPNAS12', 'VALUE (R$)')
    
#Indices de Confiança
#Índice de Confiança do Consumidor da Fecomercio/SP
ICCBrasil = ipeadataValor("FCESP12_IIC12", "VALUE (-)")

#Índice de Confiança do Empre´sario Industrial da CNI
ICEIBrasil = ipeadataValor("CNI12_ICEIGER12", "VALUE (-)")
    
#Divida Interna Liquida sobre o PIB (%) do governo federal
#e Banco Central
dividaintliqPIB = ipeadataValor('BM12_DINGFY12', "VALUE ((% PIB))")

#IGP-M na Variação Mensal
IGPMMensal = ipeadataValor('IGP12_IGPMG12', 'VALUE ((% a.m.))')

#IGP-M na Variação Acumulada em 12 meses
mensal = ipeadataMensal('IGP12_IGPMG12', 'VALUE ((% a.m.))')
IGPM12m = dozemeses(mensal)
del mensal

#IGP-10 na Variação Mensal
IGP10Mensal = ipeadataValor('IGP12_IGP1012', 'VALUE (-)')

#IGP-10 na Variação Acumulada em 12 meses
mensal = ipeadataMensal('IGP12_IGP1012', 'VALUE (-)')
IGP1012m = dozemeses(mensal)
del mensal

#IGP-DI na Variação Mensal
IGPDIMensal = ipeadataValor('IGP12_IGPDIG12', 'VALUE ((% a.m.))')

#IGP-DI na Variação Acumulada em 12 meses
mensal = ipeadataMensal('IGP12_IGPDIG12', 'VALUE ((% a.m.))')
IGPDI12m = dozemeses(mensal)
del mensal
