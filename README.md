## Extração de Dados Macroeconômicos
Códigos para extração e tratamento de dados macroeconômicos do Brasil, EUA, Europa, China e outros que forem de relevância para análises econômicas. O código é feito no Python e os dados são obtidos, na maioria dos casos, via endpoints. O objetivo é retornar, essencialmente, duas colunas: data (em string) e valor. Isso porque os códigos aqui postos são baseados num projeto particular denominado 'Atlas', a qual não possui repositório público. 

Abaixo, os dados disponíveis estão organizados por fonte e país. 

## IBGE/Brasil
Os dados do IBGE são de suma importância para a análise econômica do Brasil, com dados que permitem analisar e prever variáveis da atividade econômica, da inflação, do emprego, etc. Para tanto, produzi 3 funções: <kbd>tratPIB</kbd>, que é utilizado exclusivamente para extrair e tratar os dados do PIB; <kbd>tratPIM</kbd>, que é usado para extrair e tratar os dados da PIM-PF; e <kbd>tratIBGEGeral</kbd>, que serve para todos as outras tabelas que extrai e tratei.

Caso você deseje extrair outra tabela do SIDRA, este link fornece a documentação necessária para construir o endpoint e extrair os dados: https://apisidra.ibge.gov.br/. O IBGE não exige chave/key para extrair os dados. 

Os dados que foram extraidos no código <kbd>extracaoIBGE.py</kbd> são:
- PMC na Variação Mensal do Setor de Construção;
  PMC na Variação Mensal do Setor de Varejo;
- PMC na Variação Mensal do Setor de Varejo Ampliado;
- PMC na Variação Mensal do Setor de Veículos;
- PMC na Variação Acumulada no Ano do Setor de Construção;
- PMC na Variação Acumulada no Ano do Setor de Varejo;
- PMC na Variação Acumulada no Ano do Setor de Varejo Ampliado;
- PMC na Variação Acumulada no Ano do Setor de Veículos;
- PMC na Variação Acumulada em 12 meses do Setor de Construção;
- PMC na Variação Acumulada em 12 meses do Setor de Varejo;
- PMC na Variação Acumulada em 12 meses do Setor de Varejo Ampliado;
- PMC na Variação Acumulada em 12 meses do Setor de Veículos;
- PMS na Variação Mensal;
- PMS na Variação Mensal (comparado ao mesmo mês do ano anterior);
- PMS na Variação Acumulada no Ano;
- PMS na Variação Acumulada em 12 meses;
- IPCA na Variação Mensal;
- IPCA na Variação Acumulada no Ano;
- IPCA na Variação Acumulada em 12 meses;
- INPC na Variação Mensal;
- INPC na Variação Acumulada no Ano;
- INPC na Variação Acumulada em 12 meses;
- IPCA-15 na Variação Mensal;
- IPCA-15 na Variação Acumulada no Ano;
- IPCA-15 na Variação Acumulada em 12 meses;
- PPI na Variação Mensal;
- PPI na Variação Acumulada no Ano;
- PPI na Variação Acumulada em 12 meses;
- PIM-PF da Indústria Geral na Variação Mensal;
- PIM-PF da Indústria Geral na Variação Acumulada no Ano;
- PIM-PF da Indústria Geral na Variação Acumulada em 12 meses;
- PIB Total na Comparação com o mesmo Trimestre do Ano Anterior;
- PIB Total na Comparação com o Trimestre Imediatamente Anterior;
- PIB Total no Acumulado no Ano;
- PIB Total no Acumulado em 4 Trimestres.



