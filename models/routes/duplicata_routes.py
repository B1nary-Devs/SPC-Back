from flask import Blueprint, request, jsonify
from datetime import datetime
from models.app import mongo

duplicata = Blueprint('duplicata', __name__)  # Rota para acesso '/duplicata'
duplicata_collection = mongo.db.duplicatas  # Coleção de duplicatas no MongoDB

# Rota para criar uma nova duplicata
@duplicata.route('/createDuplicata', methods=['POST'])
def create_duplicata():
    try:
        data = request.get_json(force=True)

        duplicata_id = data.get('duplicata_id')

        duplicataExists = duplicata_collection.find_one({'duplicata_id': duplicata_id})
        if duplicataExists:
            return jsonify({'error': f'Duplicata com ID {duplicata_id} já existe'}), 400

        duplicata_data = {
            'duplicata_nome': data['duplicata_nome'],
            'duplicata_id': duplicata_id,
            'duplicata_data_inicial': data['duplicata_data_inicial'],
            'duplicata_vencimento': data['duplicata_vencimento'],
            'duplicata_status': data['duplicata_status']
        }

        duplicata_collection.insert_one(duplicata_data)

        return jsonify({'message': 'Duplicata criada com sucesso!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para listar todas as duplicatas
@duplicata.route('/listDuplicatas', methods=['GET'])
def list_duplicatas():
    try:
        duplicatas = duplicata_collection.find({})
        duplicatas_json = [{**duplicata, '_id': str(duplicata['_id'])} for duplicata in duplicatas]

        return jsonify(duplicatas_json), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para obter uma duplicata específica por ID
@duplicata.route('/<duplicata_id>', methods=['GET'])
def get_duplicata(duplicata_id):
    try:
        duplicata = duplicata_collection.find_one({'duplicata_id': duplicata_id})

        if not duplicata:
            return jsonify({'error': 'Duplicata não encontrada!'}), 404

        duplicata['_id'] = str(duplicata['_id'])

        return jsonify(duplicata), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para atualizar uma duplicata existente por ID
@duplicata.route('/<duplicata_id>/updateDuplicata', methods=['PUT'])
def update_duplicata(duplicata_id):
    try:
        data = request.get_json(force=True)
        duplicata = duplicata_collection.find_one({'duplicata_id': duplicata_id})

        if not duplicata:
            return jsonify({'error': 'Duplicata não encontrada!'}), 404

        update_fields = {}
        if 'duplicata_nome' in data:
            update_fields['duplicata_nome'] = data['duplicata_nome']
        if 'duplicata_data_inicial' in data:
            update_fields['duplicata_data_inicial'] = data['duplicata_data_inicial']
        if 'duplicata_vencimento' in data:
            update_fields['duplicata_vencimento'] = data['duplicata_vencimento']
        if 'duplicata_status' in data:
            update_fields['duplicata_status'] = data['duplicata_status']

        if not update_fields:
            return jsonify({'error': 'Nenhum campo para atualizar.'}), 400

        result = duplicata_collection.update_one({'duplicata_id': duplicata_id}, {'$set': update_fields})

        if result.matched_count == 0:
            return jsonify({'error': 'Duplicata não encontrada!'}), 404

        return jsonify({'message': 'Duplicata atualizada com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para deletar uma duplicata por ID
@duplicata.route('/<duplicata_id>/deleteDuplicata', methods=['DELETE'])
def delete_duplicata(duplicata_id):
    try:
        duplicata = duplicata_collection.find_one({'duplicata_id': duplicata_id})

        if not duplicata:
            return jsonify({'error': 'Duplicata não encontrada!'}), 404

        result = duplicata_collection.delete_one({'duplicata_id': duplicata_id})

        if result.deleted_count == 0:
            return jsonify({'error': 'Não foi possível excluir a duplicata.'}), 500

        return jsonify({'message': 'Duplicata excluída com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Função auxiliar para verificar e atualizar status de vencimento
def verificar_e_atualizar_status_duplicata(duplicata):
    try:
        data_vencimento = duplicata.get('duplicata_vencimento')
        duplicata_status = duplicata.get('duplicata_status')

        if data_vencimento:
            data_vencimento = datetime.strptime(data_vencimento, '%Y-%m-%d')
            if data_vencimento < datetime.now() and duplicata_status != 'vencido':
                # Atualiza para "vencido" se o vencimento já passou
                duplicata_collection.update_one(
                    {'duplicata_id': duplicata['duplicata_id']},
                    {'$set': {'duplicata_status': 'vencido'}}
                )
                duplicata['duplicata_status'] = 'vencido'
        return duplicata

    except Exception as e:
        print(f'Erro ao verificar vencimento: {e}')
        return None

# Rota para listar duplicatas por status
@duplicata.route('/duplicatas/status/<string:status>', methods=['GET'])
def list_duplicatas_por_status(status):
    try:
        # Data atual para comparação
        data_atual = datetime.now()
        filtro = {}

        if status == 'aberto':
            filtro = {'duplicata_status': 'aberto'}
        elif status == 'a vencer':
            filtro = {
                'duplicata_vencimento': {'$gte': data_atual.strftime('%Y-%m-%d')},
                'duplicata_status': {'$ne': 'vencido'}
            }
        elif status == 'vencido':
            filtro = {'duplicata_status': 'vencido'}
        else:
            return jsonify({'error': 'Status inválido! Use "aberto", "a vencer" ou "vencido".'}), 400

        duplicatas = duplicata_collection.find(filtro)
        duplicatas_json = [{**duplicata, '_id': str(duplicata['_id'])} for duplicata in duplicatas]
        duplicatas_atualizadas = [verificar_e_atualizar_status_duplicata(duplicata) for duplicata in duplicatas_json]

        return jsonify(duplicatas_atualizadas), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500