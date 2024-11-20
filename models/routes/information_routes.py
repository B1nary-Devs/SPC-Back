from datetime import datetime
from flask import Blueprint, jsonify, request
from models.app import mongo
from werkzeug.utils import secure_filename
import os
from models.utils import previsao

# Inicialização da coleção MongoDB
information = Blueprint('information', __name__)
information_collection = mongo.db.information

# Diretório onde o arquivo tratado está salvo
UPLOAD_FOLDER = r'.\models\utils\files'
APPROVED_FILE = ''


# Rota para criar uma nova informação
@information.route('/create_with_csv', methods=['POST'])
def create_information():
    try:
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
        
        file = request.files['file']
        
        # Se o arquivo não tiver nome (campo obrigatório)
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400
        
         # Verifique se o arquivo é um Excel
        if file and file.filename.endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            upload_folder = './models/utils/files'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
        
        df_tratado, previsao = previsao(filepath)

        mes_atual = datetime.now().month
        df_mes_atual = df_tratado[df_tratado['mes_referencia'].dt.month == mes_atual]

        APPROVED_FILE = filename

        return jsonify({
            'message': 'Arquivo processado com sucesso!',
            'Previsto': previsao,
            'Recebido': df_mes_atual
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para criar uma nova informação
@information.route('/create_without_csv', methods=['GET'])
def create_information():
    try:
        filepath = os.path.join(UPLOAD_FOLDER, APPROVED_FILE)

        # Verifica se o arquivo existe antes de tentar processá-lo
        if not os.path.exists(filepath):
            return jsonify({'error': 'Arquivo tratado não encontrado. Por favor, faça o upload primeiro.'}), 404

        df_tratado, previsao = previsao(filepath)

        mes_atual = datetime.now().month
        df_mes_atual = df_tratado[df_tratado['mes_referencia'].dt.month == mes_atual]

        return jsonify({
            'message': 'Arquivo processado com sucesso!',
            'Previsto': previsao,
            'Recebido': df_mes_atual
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500