from datetime import datetime
from flask import Blueprint, jsonify, request
from models.app import mongo
import pandas as pd
from werkzeug.utils import secure_filename
import os
from models.utils.previsao import previsao_spc
import numpy as np

# Inicialização da coleção MongoDB
information = Blueprint('information', __name__)

# Diretório onde o arquivo tratado está salvo
UPLOAD_FOLDER = r'.\models\utils\files'
APPROVED_FILE = None  

# Rota para criar uma nova informação
@information.route('/create_with_csv', methods=['POST'])
def create_with_csv():
    global APPROVED_FILE
    try:
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
        
        file = request.files['file']
        
        # Se o arquivo não tiver nome (campo obrigatório)
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400

         # Verifique se o arquivo é um Excel
        if file and file.filename.endswith(('.xlsx', '.xls', '.csv')):
            filename = secure_filename(file.filename)
            upload_folder = './models/utils/files/'
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
        
        df = pd.read_csv(filepath)
        df_tratado, previsao = previsao_spc(df)

        # mes_atual = datetime.now().month
        # df_mes_atual = df_tratado[df_tratado['mes_referencia'] == mes_atual]
        # df_mes_atual = df_mes_atual

        APPROVED_FILE = filename
        
        previsao = previsao.tolist() if isinstance(previsao, (np.ndarray)) else previsao
        df_tratadoRegistro = df_tratado['total_registros'].tolist()
        df_tratadoMes = df_tratado['mes_referencia'].tolist()

        # Cria uma lista de dicionários para combinar mês e registro
        meses_registros = []
        for mes, registro in zip(df_tratadoMes, df_tratadoRegistro):
            meses_registros.append({'Mes': mes, 'Registro': registro })

        return jsonify({
            'message': 'Arquivo processado com sucesso!',
            'Previsto': previsao,
            'Mes Previsto':  meses_registros
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para criar uma nova informação
@information.route('/create_without_csv', methods=['GET'])
def create_without_csv():
    global APPROVED_FILE
    try:
        filepath = os.path.join(UPLOAD_FOLDER, APPROVED_FILE)

        # Verifica se o arquivo existe antes de tentar processá-lo
        if not os.path.exists(filepath):
            return jsonify({'error': 'Arquivo tratado não encontrado. Por favor, faça o upload primeiro.'}), 404
        
        df = pd.read_csv(filepath)
        df_tratado, previsao = previsao_spc(df)

        mes_atual = datetime.now().month
        df_mes_atual = df_tratado[df_tratado['mes_referencia'] == mes_atual]
        df_mes_atual = df_mes_atual['total_registros'].tolist()

        previsao = previsao.tolist() if isinstance(previsao, (np.ndarray)) else previsao

        return jsonify({
            'message': 'Arquivo processado com sucesso!',
            'Previsto': previsao,
            'Recebido': df_mes_atual
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500