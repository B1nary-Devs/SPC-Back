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
prevision_collection = mongo.db.prevision 

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
        
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month
        mes_futuro = (datetime.now().month % 12) + 1
        mes_previsao =  [mes_atual, mes_futuro ]
        
        if df_tratado['mes_referencia'].eq(mes_atual).any():
            df_mes_atual = df_tratado[df_tratado['mes_referencia'] == mes_atual]
            df_mes_atual = df_mes_atual['total_registros']
        else:
            df_mes_atual = 0
        
        
        APPROVED_FILE = filename
        
        #update mongo
        prevision_collection.update_one(
            {'ano': ano_atual, 'dados.mes': mes_atual}, 
            {'$set': {
                'dados.$.previsto': previsao[0],
                'dados.$.recebido': df_mes_atual
                }},
            upsert=True
        )
        prevision_collection.update_one(
            {'ano': ano_atual, 'dados.mes': mes_futuro}, 
            {'$set': {
                'dados.$.previsto': previsao[1]
            }}
        )
        
        return jsonify({'meses': mes_previsao, 'previsoes': previsao}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para criar uma nova informação
@information.route('/previsions', methods=['GET'])
def get_previsions():
    try:
        insertPrevisao()
        
        ano_atual = datetime.now().year
        
        # Recupera as previsões atualizadas do banco de dados
        prevision = prevision_collection.find({'ano': ano_atual})

        # Converte para um formato serializável (incluindo a conversão do _id para string)
        prevision_json = [{**previsions, '_id': str(previsions['_id'])} for previsions in prevision]
        
        return jsonify({'previsao': prevision_json}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500    
        

# # Rota para criar uma nova informação
# @information.route('/create_without_csv', methods=['GET'])
# def create_without_csv():
#     global APPROVED_FILE
#     try:
#         filepath = os.path.join(UPLOAD_FOLDER, APPROVED_FILE)

#         # Verifica se o arquivo existe antes de tentar processá-lo
#         if not os.path.exists(filepath):
#             return jsonify({'error': 'Arquivo tratado não encontrado. Por favor, faça o upload primeiro.'}), 404
        
#         df = pd.read_csv(filepath)
#         df_tratado, previsao = previsao_spc(df)

#         mes_atual = datetime.now().month
#         df_mes_atual = df_tratado[df_tratado['mes_referencia'] == mes_atual]
#         df_mes_atual = df_mes_atual['total_registros'].tolist()

#         previsao = previsao.tolist() if isinstance(previsao, (np.ndarray)) else previsao

#         return jsonify({
#             'message': 'Arquivo processado com sucesso!',
#             'Previsto': previsao,
#             'Recebido': df_mes_atual
#         }), 201

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


def insertPrevisao():
    try:
        prevision = [{
            'ano': 2024,
             'dados': [
                {'mes': 1, 'previsto': 0, 'recebido': 3208},
                {'mes': 2, 'previsto': 0, 'recebido': 26003},
                {'mes': 3, 'previsto': 0, 'recebido': 114707},
                {'mes': 4, 'previsto': 0, 'recebido': 12250},
                {'mes': 5, 'previsto': 0, 'recebido': 4673},
                {'mes': 6, 'previsto': 7165, 'recebido': 7319},
                {'mes': 7, 'previsto': 6442, 'recebido': 5499},
                {'mes': 8, 'previsto': 6054, 'recebido': 7471},
                {'mes': 9, 'previsto': 6786, 'recebido': 0},
                {'mes': 10, 'previsto': 7004, 'recebido': 0},
                {'mes': 11, 'previsto': 0, 'recebido': 0},
                {'mes': 12, 'previsto': 0, 'recebido': 0}
            ]
        }]
        for x in prevision:
            existing_prevision = prevision_collection.find_one({'ano': x['ano']})

            if (existing_prevision):
                continue
            else:
                prevision_collection.insert_one(x)

        return
    except Exception as e:
        print(f"Erro: {str(e)}")