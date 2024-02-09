# -*- coding: utf-8 -*-
"""
@author: nicolasledurf
"""
import yfinance as yf
import pandas as pd

#Função para extrair os dados do yahooFinance
def yahooFinance(ticket):
    url = yf.Ticker(ticket)
    hist = url.history(period="24mo")
    hist = hist.reset_index(inplace=False)
    hist = hist[['Date', 'Close']]
    hist = hist.rename(columns={'Date': 'data', 'Close': 'valor'})
    hist['data'] = pd.to_datetime(hist['data'], format='%Y-%m-%d').apply(lambda x: x.strftime('%Y-%m-%d'))
    return hist

#Extração do DXY
dxy = yahooFinance('DX-Y.NYB', 'dxy')
    
#Preços Futuros
#Extração do Preço Futuro da Soja fornecido pelo CBOT
sojaFuturoCBOT = yahooFinance("ZS=F")

#Extração do Preço Futuro do Milho fornecido pelo CBOT
milhoFuturoCBOT = yahooFinance("ZC=F")
    
#Extração do Preço Futuro do Petróleo fornecido pelo CBOT
brentLastDay = yahooFinance("CL=F")
