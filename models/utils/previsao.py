import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

def prever_proximos_meses(df, order=(1,1,0)):
    # Escolher o modelo ARIMA com a ordem fornecida
    modelo = ARIMA(df['total_registros'], order=order)
    model_fit = modelo.fit()

    #Previsão do proximo mes
    forecast = model_fit.forecast(steps=1)

    # Convertendo o numpy.ndarray para lista de Python
    forecast_list = forecast.tolist()

    # Convertendo para tipos nativos (int) para evitar o erro de serialização
    forecast_list = [int(item) for item in forecast_list]

    return forecast_list


def tratamentoDado(df):
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Extrai o mês da coluna de datas
    df['mes_referencia'] = df['created_at'].dt.month
    # Extrai o ano da coluna de datas
    df['ano_referencia'] = df['created_at'].dt.year

    # Agora podemos agrupar por mês e período (antes ou após o dia 15) e contar os registros (total_registros)
    df_mensal = df.groupby(['mes_referencia', 'ano_referencia']).agg(
        total_registros=('id_x', 'size')
    ).reset_index()

    df_anual = df_mensal[df_mensal['ano_referencia'] == 2024]

    return df_anual

def previsao_spc(df):
    df_tratado = tratamentoDado(df)
    previsao = prever_proximos_meses(df_tratado)
    return previsao
