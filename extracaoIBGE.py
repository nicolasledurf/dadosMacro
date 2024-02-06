# -*- coding: utf-8 -*-
"""
@author: nicolasledurf
"""
import requests as rq
import pandas as pd
import ssl

#Função para garantir que as requisições funcionem 
#independentemente das questões de segurança do site
class TLSAdapter(rq.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.options |= 0x4
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
    

#Função para solicitar acesso aos dados do IBGE e transformar em json
def obtIBGE(adress):
    with rq.session() as s:
        s.mount("https://", TLSAdapter())
        table = s.get(adress).json()
        
    return table

#Função para transformar o formato da data que vem do IBGE para qual eu prefiro
def textoParaData(valor):
  return valor[:-2] + '-' + valor[-2:] + '-01'

#Função para transformar a string do trimestre em formato mais adequado
#para os meus usos
def stringTrimestre(valor):
    return valor[-2:] + '/' + valor[:-2]

#Função para transformar a string do trimestre em formato de data
def trimParaData(valor):
    if valor[-2:] == "01":
        return '01-' + '03' + '-' + valor[:-2]
    if valor[-2:] == "02":
        return '01-' + '06' + '-' + valor[:-2]
    if valor[-2:] == "03":
        return '01-' + '09' + '-' + valor[:-2]
    if valor[-2:] == "04":
        return '01-' + '12' + '-' + valor[:-2]

#Função para obter e tratar os dados do PIB fornecidos pelo IBGE. 
def tratPIB(endpoint): 
   data = obtIBGE(endpoint)
   data = pd.DataFrame(data)
   data.columns.name = None
   data = data[1:]
    
   data = data.rename(columns={'D3C': 'trimestre', 'V': 'valor', 'D4N': 'setor'})
   data = data[data['valor'] != "-"]
   data = data[data['valor'] != "..."]

   data['valor'] = data['valor'].astype(float)
   data['data'] = data['trimestre'].apply(trimParaData)

   data['data'] = pd.to_datetime(data['data'], format='%d-%m-%Y')   
   data['trimestre'] = data['trimestre'].apply(stringTrimestre)
   data = data[data['setor'] == 'PIB a preços de mercado']

   data = data[['valor', 'data']]
   data = data[pd.notnull(data['data'])]

   data['data'] = data['data'].apply(lambda x: x.strftime('%Y-%m-%d'))
   return data

#Função para obter e tratar os dados da Pesquisa Industrial Mensal (PIM)
def tratPIM(endpoint): 
    data = obtIBGE(endpoint)
    data = pd.DataFrame(data)
    data = data.drop(
           data.columns[[0, 1, 2, 3, 5, 6, 7, 8, 10]], axis=1)
    data.columns.name = None
    data = data[1:]
    data = data.rename(columns={'V': 'valor', 'D4N': 'setor'})
    data['data'] = data['D3C'].apply(textoParaData)

    data = data[data['valor'] != "-"]
    data = data[data['valor'] != "..."]
    data['valor'] = data['valor'].astype(float)

    data = data[data['setor'] == '1 Indústria geral']
    data = data[['valor', 'data']]
    return data
        
#Função genérica para obter e tratar dados do IBGE. Funciona para a maioria dos endpoints.
def tratIBGEGeral(endpoint):
    data = obtIBGE(endpoint) 
        
    data = pd.DataFrame(data)
    data.columns.name = None
    data = data[1:]

    data['data'] = data['D3C'].apply(textoParaData)
    data = data.rename(columns={'V': 'valor'})

    data = data[data['valor'] != "-"]
    data = data[data['valor'] != "..."]
    data['valor'] = data['valor'].astype(float)
    
    data = data[['valor', 'data']]
    return data

#E quais são os dados que podemos obter com as funções que foram demonstradas acima?
#PMC na Variação Mensal do setor de Construção
PMCMensalConst = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8757/N1/1/v/11708/p/all/C11046/56732')

#PMC na Variação Mensal do setor de Varejo    
PMCMensalVar = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8880/N1/1/v/11708/p/all/C11046/56734')

#PMC na Variação Mensal do setor de Varejo (comparado ao mesmo mês do ano anterior)
PMCMensalAnualVar = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8880/N1/1/v/11708/p/all/C11046/56734')

#PMC na Variação Mensal do Setor de Varejo Ampliado;
PMCMensalVarAmp = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8881/N1/1/v/11709/p/all/C11046/56736')

#PMC na Variação Mensal do Setor de Veículos;
PMCMensalVeic = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8884/N1/1/v/11708/p/all/C11046/56738')

#PMC na Variação Acumulada no Ano do Setor de Construção
PMCAnualConst = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8757/N1/1/v/11710/p/all/C11046/56732')

#PMC na Variação Acumulada no Ano do Setor de Varejo
PMCAnualVar = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8880/N1/1/v/11710/p/all/C11046/56734')

#PMC na Variação Acumulada no Ano do Setor de Varejo Ampliado
PMCAnualVarAmp = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8881/N1/1/v/11710/p/all/C11046/56736')

#PMC na Variação Acumulada no Ano do Setor de Veículos
PMCAnualVeic = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8884/N1/1/v/11710/p/all/C11046/56738')

#PMC na Variação Acumulada em 12 meses do Setor de Construção
PMC12mMConst = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8757/N1/1/v/11711/p/all/C11046/56732')

#PMC na Variação Acumulada em 12 meses do Setor de Varejo  
PMC12mVar = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8880/N1/1/v/11711/p/all/C11046/56734')

#PMC na Variação Acumulada em 12 meses do Setor de Varejo Ampliado; 
PMC12mVarAmp = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8881/N1/1/v/11711/p/all/C11046/56736')

#PMC na Variação Acumulada em 12 meses do Setor de Veículos    
PMC12mVeic = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8884/N1/1/v/11711/p/all/C11046/56738')

#PMS na Variação Mensal
PMSMensal = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8688/N1/1/v/11623/p/all/C11046/56726/C12355/107071')

#PMS na Variação Mensal (comparado ao mesmo mês do ano anterior)
PMSMensalAnual = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8688/N1/1/v/11624/p/all/C11046/56726/C12355/107071')

#PMS na Variação Acumulada no Ano
PMSAnual = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8688/N1/1/v/11625/p/all/C11046/56726/C12355/107071')

#PMS na Variação Acumulada em 12 meses
PMS12m = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/8688/N1/1/v/11626/p/all/C11046/56726/C12355/107071')

#IPCA na Variação Mensal
IPCAMensal = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/1737/N1/1/v/63/p/all')

#IPCA na Variação Acumulada no Ano
IPCAAnual = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/1737/N1/1/v/69/p/all')

#IPCA na Variação Acumulada em 12 meses    
IPCA12m = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/1737/N1/1/v/2265/p/all')

#INPC na Variação Mensal
INPCMensal = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/1736/N1/1/v/44/p/all')

#INPC na Variação Acumulada no Ano
INPCAnual = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/1736/N1/1/v/68/p/all')

#INPC na Variação Acumulada em 12 meses  
INPC12m = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/1736/N1/1/v/2292/p/all')

#IPCA-15 na Variação Mensal
IPCA15Mensal = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/7062/N1/1/v/355/p/all')

#IPCA-15 na Variação Acumulada no Ano
IPCA15Anual = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/7062/N1/1/v/356/p/all')

# IPCA-15 na Variação Acumulada em 12 meses 
IPCA1512m = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/7062/N1/1/v/1120/p/all')
    
#PPI na Variação Mensal
PPIBrasilMensal = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/6903/N1/1/v/1396/p/all/C842/46608')

#PPI na Variação Acumulada no Ano
PPIBrasilAnual = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/6903/N1/1/v/1395/p/all/C842/46608')

#PPI na Variação Acumulada em 12 meses    
PPIBrasil12m = tratIBGEGeral('http://api.sidra.ibge.gov.br/values/t/6903/N1/1/v/1394/p/all/C842/46608')
    
#PIM-PF da Indústria Geral na Variação Mensal
PIMPFMensal = tratPIM('http://api.sidra.ibge.gov.br/values/t/8888/N1/1/v/11601/p/all/C544/129314')

#PIM-PF da Indústria Geral na Variação Acumulada no Ano
PIMPFAnual = tratPIM('http://api.sidra.ibge.gov.br/values/t/8888/N1/1/v/11603/p/all/C544/129314')

#PIM-PF da Indústria Geral na Variação Acumulada em 12 meses
PIMPF12m = tratPIM('http://api.sidra.ibge.gov.br/values/t/8888/N1/1/v/11604/p/all/C544/129314')

#PIB Total na Comparação com o mesmo Trimestre do Ano Anterior
PIBTrimAnterior = tratPIB('http://api.sidra.ibge.gov.br/values/t/5932/N1/1/v/6561/p/all/C11255/all')

#PIB Total na Comparação com o Trimestre Imediatamente Anterior    
PIBTrimImed = tratPIB('http://api.sidra.ibge.gov.br/values/t/5932/N1/1/v/6564/p/all/C11255/all')

#PIB Total no Acumulado no Ano
PIBAnual = tratPIB('http://api.sidra.ibge.gov.br/values/t/5932/N1/1/v/6563/p/all/C11255/all')

#PIB Total no Acumulado em 4 Trimestres
PIB4Trimestres = tratPIB('http://api.sidra.ibge.gov.br/values/t/5932/N1/1/v/6562/p/all/C11255/all')