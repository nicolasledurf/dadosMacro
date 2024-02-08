## Extração de Dados Macroeconômicos
Códigos para extração e tratamento de dados macroeconômicos do Brasil, EUA, Europa, China e outros que forem de relevância para análises econômicas. O código é feito no Python e os dados são obtidos, na maioria dos casos, via endpoints. O objetivo é retornar, essencialmente, duas colunas: data (em string) e valor. Isso porque os códigos aqui postos são baseados num projeto particular denominado 'Atlas', a qual não possui repositório público. 

*É importante destacar que os códigos são guias e são baseados em outros projetos, e o usuário precisará alterar conforme a sua necessidade. Muitas das coisas que programei foram feitas com uma determinada finalidade, então poderá haver coisa redundante ou inútil no código. Devido ao trabalho e tempo que isso exigiria, não foquei em adpatar os códigos para que tivessem uma finalidade própria*

Abaixo, os dados disponíveis estão organizados por fonte e país. 

## IBGE/Brasil
Os dados do IBGE são de suma importância para a análise econômica do Brasil, com dados que permitem analisar e prever variáveis da atividade econômica, da inflação, do emprego, etc. Para tanto, produzi 3 funções: <kbd>tratPIB</kbd>, que é utilizado exclusivamente para extrair e tratar os dados do PIB; <kbd>tratPIM</kbd>, que é usado para extrair e tratar os dados da PIM-PF; e <kbd>tratIBGEGeral</kbd>, que serve para todos as outras tabelas que extrai e tratei.

Caso você deseje extrair outra tabela do SIDRA, este link fornece a documentação necessária para construir o endpoint e extrair os dados: https://apisidra.ibge.gov.br/. O IBGE não exige chave/key para extrair os dados. 

Os dados que foram extraidos no código [extracaoIBGE.py](extracaoIBGE.py) são:
- PMC na Variação Mensal, Anual e em 12 meses do Setor de Construção;
  PMC na Variação Mensal, Anual e em 12 meses do Setor de Varejo;
- PMC na Variação Mensal, Anual e em 12 meses do Setor de Varejo Ampliado;
- PMC na Variação Mensal, Anual e em 12 meses do Setor de Veículos;
- PMS na Variação Mensal, Anual e em 12 meses;
- PMS na Variação Mensal (comparado ao mesmo mês do ano anterior);
- IPCA na Variação Mensal, Anual e em 12 meses;
- INPC na Variação Mensal, Anual e em 12 meses;
- IPCA-15 na Variação Mensal, Anual e em 12 meses;
- PPI na Variação Mensal, Anual e em 12 meses;
- PIM-PF da Indústria Geral na Variação Mensal, Anual e em 12 meses;
- PIB Total na Comparação com o mesmo Trimestre do Ano Anterior;
- PIB Total na Comparação com o Trimestre Imediatamente Anterior;
- PIB Total no Acumulado no Ano;
- PIB Total no Acumulado em 4 Trimestres.

## Ipeadata/Brasil
O Ipeadata é, sem sombra de dúvidas, uma das melhores bases de dados disponíveis no Brasil. Para pesquisadores e programadores, os pacotes disponibilizados pela comunidade (utilizo o <kbd>ipeadatapy</kbd>) permitem acesso a base de dados que de outra forma seriam complicados de se acessar e atualizar automaticamente. Portanto, com vista para o código [extracaoIpeadata.py](extracaoIpeadata.py) obtive os seguintes dados:
- SELIC;
- Operações de Crédito, Saldo da Carteira, Recursos Livres Total na Variação Mensal/Brasil;
- Operações de Crédito, Saldo da Carteira Total na Variação Mensal/Brasil;
- IBC-Br Índice Real Dessazonalizado (2002=100) na Variação Mensal;
- M0: papel-moeda emitido em milhões de reais;
- M1: Depósitos à Vista + PMPP em milhões de reais;
- M2: M1 + Poupança + Títulos Privados em milhões de reais;
- M3: M2 + Cotas de Fundos + Operações Comprom. de Títulos Públicos e Federais em milhões de reais;
- M4: M3 + Títulos emitidos pelo Governo Federal em milhões de reais;
- Dívida Interna Federal, fora do BC, posição em carteira, fim de período, em milhões de reais;
- Necessidade de Financiamento do Setor Público Acum. em 12 meses em  milhões de reais;
- Índice de Confiança do Consumidor da Fecomercio/SP;
- Índice de Confiança do Empresário Industrial da CNI;
- Divida Interna Liquida sobre o PIB (%) do governo federal e Banco Central;
- IGP-M na Variação Mensal;
- IGP-M na Variação Acumulada em 12 meses;
- IGP-10 na Variação Mensal;
- IGP-10 na Variação Acumulada em 12 meses;
- IGP-DI na Variação Mensal;
- IGP-DI na Variação Acumulada em 12 meses.

## FED ou FRED/USA
O FED, via FRED (https://fred.stlouisfed.org/docs/api/fred/)https://fred.stlouisfed.org/docs/api/fred/), é a melhor base de dados que encontrei para obter dados macroeconômicos dos Estados Unidos. Alguns dados são fornecidos diretamente pelo FED, mas outros apenas pertencem a outras organizações/departamentos - e estes podem demorar alguns dias para atualizar para os valores mais recentes. Para que a API do FRED funcione, é necessário que você se cadastre e obtenha uma key para a API. Os dados que estão no código [extracaoFED.py](extracaoFED.py) são: 
- Meio Monetário M1;
- Meio Monetário M2;
- payroll;
- GDP (Gross Domestic Product) em bilhões de dólares;
- GDP (Gross Domestic Product) na variação do trimestre comparado ao trimestre imediatamente anterior;
- GDP (Gross Domestic Product) na variação acumulada em 4 trimestres;
- GDP (Gross Domestic Product) na variação acumulada no ano;
- Juros de Hipoteca de 30 anos;
- Ganho Médio por Hora Trabalhada, Total Privado, na Variação Mensal;
- Ganho Médio por Hora Trabalhada, Total Privado, na Variação Acumulada no Ano;
- Variação Mensal, Acumulada no Ano e em 12 meses do CPI;
- Variação Mensal, Acumulada no Ano e em 12 meses do PCE;
- Variação Mensal, Acumulada no Ano e em 12 meses do núcleo do CPI;
- Variação Mensal, Acumulada no Ano e em 12 meses do núcleo do PCE;
- Variação Mensal, Acumulada no Ano e em 12 meses do PPI;
- Variação Mensal, Acumulada no Ano e em 12 meses da Produção Industrial;
- Variação Mensal, Acumulada no Ano e em 12 meses das Vendas no Varejo;
- Pedidos iniciais por Seguro Desemprego em pessoas;
- FFR - Taxa Básica de juros Americana, limite máximo e mínimo;
- Títulos do Tesouro Americano com vencimento em 5, 10 e 20 anos, indexados pela inflação;
- Variação de novos peiddos para manufatura: bens duráveis excento transporte;
- #Expectativa de Inflação da Universidade de Michigan.
