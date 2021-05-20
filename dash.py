# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import requests
import pandas 
import numpy 
import json
import streamlit as st

# %%
def json_to_series(text):
    keys, values = zip(*[(dct['label'], dct['value']) for dct in json.loads(text)])
    return pd.Series(values, index=keys)
''


@st.cache(allow_output_mutation=True)
def exportarVeiculos():
    index = 1
    req_total = []
    df_final = pandas.DataFrame()
    while index < 100:
        req_veiculos = requests.get("https://www.webmotors.com.br/api/search/car?url=https://www.webmotors.com.br/carros%2Fms%3Fanunciante%3DConcession%25C3%25A1ria%257CLoja%26estadocidade%3DMato%2520Grosso%2520do%2520Sul", params="actualPage=" + str(index))
        req_veiculos = json.loads(req_veiculos.text)
        try:
            req_veiculos = req_veiculos['SearchResults']
            json_str = json.dumps(req_veiculos)
            veiculos = pandas.read_json(json_str)

            tabela_especificacoes = pandas.json_normalize(veiculos['Specification'])
            veiculos = veiculos.join(other= tabela_especificacoes)

            tabela_precos = pandas.json_normalize(veiculos['Prices'])
            veiculos = veiculos.join(other= tabela_precos)

            tabela_vendedor = pandas.json_normalize(veiculos['Seller'])
            veiculos = veiculos.join(other= tabela_vendedor)

                # tabela_atributos = pandas.json_normalize(veiculos['VehicleAttributes'])
                # veiculos = veiculos.join(other= tabela_atributos)
            try:
                veiculos = veiculos.drop(columns=['Prices', 'HotDeal', 'Channels', 'VehicleAttributes', 'Media', 'Specification', 'Seller'])
                df_final = df_final.append(veiculos, ignore_index=True)
                print("Capturado página .... {}".format(index))
            except:
                print(f"Ocorreu um erro na página {index}")
        except:
            print(f"Ocorreu um erro na página {index}")
        index +=1
    return veiculos

data_load_state = st.text('Carregando dados...')
veiculos = exportarVeiculos()

data_load_state.text('')

st.sidebar.title('Opções')

st.title('Veiculos Webmotors')

# %% 
veiculos = pandas.DataFrame(data = veiculos)

# Filtro para o Preço
preco = st.sidebar.slider('Valor máximo do preço do veículo desejado', min_value=0, max_value=300000, value=50000)
odometro = st.sidebar.slider('Valor máximo de odometro', min_value=0, max_value=300000)

# Filtro para marcas
marcas = veiculos['Make.Value'].drop_duplicates()
marcas_selecionadas = st.sidebar.multiselect('Selecione a marca', marcas)


veiculos = veiculos[veiculos['SearchPrice'] < preco]
veiculos = veiculos[veiculos['Odometer'] < odometro]

veiculos = veiculos[veiculos['Make.Value'].isin(marcas_selecionadas)]

## Painel para Quantidade de Veículos
qtdVeiculosMarca = veiculos[['UniqueId', 'Make.Value', 'UniqueId']].groupby(by = veiculos['Make.Value'], as_index=True).agg('count')
qtdVeiculosMarca = qtdVeiculosMarca.drop(columns={'UniqueId'})
qtdVeiculosMarca = qtdVeiculosMarca.rename(columns={'Make.Value': 'Quantidade'})
st.sidebar.dataframe(qtdVeiculosMarca)


# Tabela para Mostrar os veículos

TabelaVeiculos = veiculos[['Make.Value', 'Model.Value', 'Transmission', 'YearModel', 'YearFabrication', 'SearchPrice', 'Odometer']]
TabelaVeiculos = TabelaVeiculos[TabelaVeiculos['SearchPrice'] < preco]

st.table(TabelaVeiculos)


# %%
#df_final.to_csv('teste2.csv', encoding="utf8")


# %%



