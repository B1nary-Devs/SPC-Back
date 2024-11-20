import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

def prever_proximos_meses(df, order=(1,1,0)):

    df = df[~df['mes_referencia'].isin([9, 10, 11, 12])]

    df['data'] = pd.to_datetime(df['mes_referencia'].astype(str), format='%m')
    df.set_index('data', inplace=True)
    df.index = pd.date_range(start=df.index[0], periods=len(df), freq='MS')
    
    # Escolher o modelo ARIMA com a ordem fornecida
    modelo = ARIMA(df['total_registros'], order=order)
    model_fit = modelo.fit()

    # Previsão para os próximos 2 meses
    forecast = model_fit.forecast(steps=1)

    previsoes = np.array(forecast)
    # Ajustar a previsão para inteiros
    previsoes = previsoes.astype(int)

    return previsoes


def tratamentoDado(df):
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Extrai o mês da coluna de datas
    df['mes_referencia'] = df['created_at'].dt.month
    
    # Agora podemos agrupar por mês e período (antes ou após o dia 15) e contar os registros (total_registros)
    df_mensal = df.groupby(['mes_referencia']).agg(
        total_registros=('id_x', 'size')
    ).reset_index()
    
    return df_mensal

def previsao_spc(df):
    df_tratado = tratamentoDado(df)
    previsao = prever_proximos_meses(df_tratado)
    return df_tratado, previsao
