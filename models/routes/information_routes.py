from flask import Blueprint, jsonify, request
from models.app import mongo
from bson import ObjectId

# Inicialização da coleção MongoDB
information = Blueprint('information', __name__)
information_collection = mongo.db.information

# Rota para criar uma nova informação
@information.route('/create', methods=['POST'])
def create_information():
    try:
        data = request.get_json(force=True)
        mes1 = data.get('mes1')
        mes2 = data.get('mes2')

        # Validação dos campos obrigatórios
        if not mes1 or not mes2:
            return jsonify({'error': 'Os campos mes1 e mes2 são obrigatórios.'}), 400

        # Inserção no MongoDB
        new_information = {'mes1': mes1, 'mes2': mes2}
        information_collection.insert_one(new_information)

        return jsonify({'message': 'Informação criada com sucesso!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para obter todas as informações
@information.route('/getAll', methods=['GET'])
def get_all_information():
    try:
        informations = information_collection.find({})
        informations_list = [{'_id': str(info['_id']), 'mes1': info['mes1'], 'mes2': info['mes2']} for info in informations]

        return jsonify(informations_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para atualizar uma informação pelo ID
@information.route('/<info_id>/update', methods=['PUT'])
def update_information(info_id):
    try:
        data = request.get_json(force=True)
        mes1 = data.get('mes1')
        mes2 = data.get('mes2')

        # Verifica se a informação existe
        info = information_collection.find_one({'_id': ObjectId(info_id)})
        if not info:
            return jsonify({'error': 'Informação não encontrada!'}), 404

        # Atualiza os campos fornecidos
        update_data = {}
        if mes1 is not None:
            update_data['mes1'] = mes1
        if mes2 is not None:
            update_data['mes2'] = mes2

        if update_data:
            information_collection.update_one({'_id': ObjectId(info_id)}, {'$set': update_data})
            return jsonify({'message': 'Informação atualizada com sucesso!'}), 200
        else:
            return jsonify({'error': 'Nenhum campo válido fornecido para atualização.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para excluir uma informação pelo ID
@information.route('/<info_id>/delete', methods=['DELETE'])
def delete_information(info_id):
    try:
        # Verifica se a informação existe
        info = information_collection.find_one({'_id': ObjectId(info_id)})
        if not info:
            return jsonify({'error': 'Informação não encontrada!'}), 404

        # Exclui a informação
        information_collection.delete_one({'_id': ObjectId(info_id)})
        return jsonify({'message': 'Informação excluída com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
