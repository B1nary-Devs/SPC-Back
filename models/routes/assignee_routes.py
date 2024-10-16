from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash
from models.app import mongo
from models.routes.user_routes import users_collection
from models.utils.email import registraEmail

assignee = Blueprint('assignee', __name__)  # Rota utilizada para acesso '/assigne'
assignee_collection = mongo.db.assigne  # colecao de usuarios do mongo db

# Rota para criação de usuarios com validacao de termos
@assignee.route('/createAssignee', methods=['POST'])
def create_assignee():
    try:
        data = request.get_json(force=True)

        # Extrai dados gerais da cessionária
        cessionaria_cnpj = data.get('cessionaria_cnpj')

        # Verifica se o CNPJ já existe na coleção de usuários
        userExists = users_collection.find_one({'cpf_cnpj': cessionaria_cnpj})
        if not userExists:
            return jsonify({'error': 'CNPJ não encontrado na base de usuários. A cessionária só pode ser criada se o CNPJ já estiver registrado como um usuário.'}), 400

        # Verifica se a cessionária já existe na coleção de cessionárias
        cessionariaExists = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})
        if cessionariaExists:
            return jsonify({'error': f'Cessionária com CNPJ {cessionariaExists["cessionaria_cnpj"]} já existe'}), 400

        # Extrai o subdocumento cessionaria_sacado, se ele for fornecido
        cessionaria_sacado = data.get('cessionaria_sacado', None)

        # Valida campos obrigatórios
        dataCessionaria = {
            'cessionaria_nome': data['cessionaria_nome'],
            'cessionaria_cnpj': cessionaria_cnpj
        }

        # Se os dados do sacado forem fornecidos, adicioná-los ao documento
        if cessionaria_sacado:
            dataCessionaria['cessionaria_sacado'] = {
                'cessionaria_sacado_id': cessionaria_sacado.get('cessionaria_sacado_id'),
                'cessionaria_sacado_score': cessionaria_sacado.get('cessionaria_sacado_score'),
                'cessionaria_sacado_duplicadas_data': cessionaria_sacado.get('cessionaria_sacado_duplicadas_data'),
                'cessionaria_sacado_duplicata_status': cessionaria_sacado.get('cessionaria_sacado_duplicata_status')
            }

        # Insere a cessionária no MongoDB
        assignee_collection.insert_one(dataCessionaria)

        return jsonify({'message': 'Cessionária criada com sucesso!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/listAssignees', methods=['GET'])
def list_assignees():
    try:
        # Busca todas as cessionárias na coleção
        cessionarias = assignee_collection.find({})
        cessionarias_json = [{**cessionaria, '_id': str(cessionaria['_id'])} for cessionaria in cessionarias]
        assignee_list = []

        for cessionaria in cessionarias_json:
            cessionaria_sacado = cessionaria.get('cessionaria_sacado', {})

            # Se o sacado existir, adiciona as informações do sacado ao resultado
            if cessionaria_sacado:
                sacado_completo = {
                    'cessionaria_sacado_id': cessionaria_sacado.get('cessionaria_sacado_id'),
                    'cessionaria_sacado_score': cessionaria_sacado.get('cessionaria_sacado_score'),
                    'cessionaria_sacado_duplicadas_data': cessionaria_sacado.get('cessionaria_sacado_duplicadas_data'),
                    'cessionaria_sacado_duplicata_status': cessionaria_sacado.get('cessionaria_sacado_duplicata_status')
                }
                cessionaria['cessionaria_sacado'] = sacado_completo
            else:
                cessionaria['cessionaria_sacado'] = None

            # Adiciona a cessionária à lista final
            assignee_list.append(cessionaria)

        # Retorna a lista completa das cessionárias
        return jsonify(assignee_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>', methods=['GET'])
def one_assignee(cessionaria_cnpj):
    try:
        # Busca a cessionária com base no CNPJ fornecido
        dataAssignee = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})

        if not dataAssignee:
            return jsonify({'error': 'Cessionária não encontrada!'}), 400

        # Converte o campo _id para string
        dataAssignee['_id'] = str(dataAssignee['_id'])

        # Inicializa a lista que será retornada
        assignee = []

        # Extrai o subdocumento de cessionaria_sacado (se houver)
        cessionaria_sacado = dataAssignee.get('cessionaria_sacado', {})

        if cessionaria_sacado:
            sacado_completo = {
                'cessionaria_sacado_id': cessionaria_sacado.get('cessionaria_sacado_id'),
                'cessionaria_sacado_score': cessionaria_sacado.get('cessionaria_sacado_score'),
                'cessionaria_sacado_duplicadas_data': cessionaria_sacado.get('cessionaria_sacado_duplicadas_data'),
                'cessionaria_sacado_duplicata_status': cessionaria_sacado.get('cessionaria_sacado_duplicata_status')
            }
            # Atualiza o subdocumento sacado da cessionária
            dataAssignee['cessionaria_sacado'] = sacado_completo
        else:
            dataAssignee['cessionaria_sacado'] = None

        # Adiciona a cessionária completa à lista final
        assignee.append(dataAssignee)

        return jsonify(assignee), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>/updateAssignee', methods=['PUT'])
def update_assignee(cessionaria_cnpj):
    try:
        data = request.get_json(force=True)
        dataAssignee = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})

        if not dataAssignee:
            return jsonify({'error': 'Cessionária não encontrada!'}), 400

        update_fields = {}

        if 'cessionaria_nome' in data:
            update_fields['cessionaria_nome'] = data['cessionaria_nome']
        if 'cessionaria_cnpj' in data:
            update_fields['cessionaria_cnpj'] = data['cessionaria_cnpj']

        # Atualiza o subdocumento cessionaria_sacado, se fornecido
        if 'cessionaria_sacado' in data:
            cessionaria_sacado = data['cessionaria_sacado']
            update_fields['cessionaria_sacado'] = {
                'cessionaria_sacado_id': cessionaria_sacado.get('cessionaria_sacado_id'),
                'cessionaria_sacado_score': cessionaria_sacado.get('cessionaria_sacado_score'),
                'cessionaria_sacado_duplicadas_data': cessionaria_sacado.get('cessionaria_sacado_duplicadas_data'),
                'cessionaria_sacado_duplicata_status': cessionaria_sacado.get('cessionaria_sacado_duplicata_status')
            }

        if not update_fields:
            return jsonify({'error': 'Nenhum campo para atualizar.'}), 400

        result = assignee_collection.update_one({'cessionaria_cnpj': cessionaria_cnpj}, {'$set': update_fields})
        if result.matched_count == 0:
            return jsonify({'error': 'Cessionária não encontrada!'}), 404

        return jsonify({'message': 'Cessionária atualizada com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>/deleteAssignee', methods=['DELETE'])
def delete_assignee(cessionaria_cnpj):
    try:
        dataAssignee = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})

        if not dataAssignee:
            return jsonify({'error': 'Cessionária não encontrada!'}), 400

        result = assignee_collection.delete_one({'cessionaria_cnpj': cessionaria_cnpj})

        if result.deleted_count == 0:
            return jsonify({'error': 'Não foi possível excluir a cessionária.'}), 500

        return jsonify({'message': 'Cessionária excluída com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>/addSacado', methods=['PUT'])
def add_sacado(cessionaria_cnpj):
    try:
        # Verfica se a cessionária existe
        cessionaria = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})

        if not cessionaria:
            return jsonify({'error': 'Cessionária não encontrada!'}), 404

        # Obtem os dados do sacado do request
        data = request.get_json(force=True)
        cessionaria_sacado = data.get('cessionaria_sacado', {})

        # Verifica se os dados do sacado foram fornecidos corretamente
        if not cessionaria_sacado:
            return jsonify({'error': 'Os dados do sacado são obrigatórios!'}), 400

        # Atualiza ou insere os dados do sacado na cessionaria existente
        update_fields = {
            'cessionaria_sacado': {
                'cessionaria_sacado_id': cessionaria_sacado.get('cessionaria_sacado_id'),
                'cessionaria_sacado_score': cessionaria_sacado.get('cessionaria_sacado_score'),
                'cessionaria_sacado_duplicadas_data': cessionaria_sacado.get('cessionaria_sacado_duplicadas_data'),
                'cessionaria_sacado_duplicata_status': cessionaria_sacado.get('cessionaria_sacado_duplicata_status')
            }
        }

        # Atualiza a cessionaria existente no banco de dados
        result = assignee_collection.update_one(
            {'cessionaria_cnpj': cessionaria_cnpj},
            {'$set': update_fields}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Não foi possível atualizar o sacado para a cessionária.'}), 500

        return jsonify({'message': 'Sacado adicionado/atualizado com sucesso para a cessionária!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


