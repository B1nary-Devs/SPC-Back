from flask import Blueprint, request, jsonify
from datetime import datetime
from models.app import mongo


user_term = Blueprint('user_term', __name__)# Rota utilizada para acesso '/user_terms'
users_collection = mongo.db.usuario # colecao de termos do mongo db


# Rota para inserir um novo termo ou versao do usuario
@user_term.route('/<user_cpf_cnpj>/insertUserTerm', methods=['POST'])
def insert__user_terms(user_cpf_cnpj):
    try:
        data = request.get_json(force=True)

        dataUser = users_collection.find_one({'cpf_cnpj': user_cpf_cnpj})
        if not dataUser:
            return jsonify({'error': 'Usuario não encontrado!'}), 400
        
        termoExist = dataUser['termos']
        for x in termoExist:
            if (x['nome_termo'] == data['nome_termo']) and (x['versao'] == data['versao']):
                return jsonify({'error': 'Termo e Condicao ja cadastrado!'}), 400

        dataUserTerm = {
            'nome_termo': data['nome_termo'],
            'prioridade': data['prioridade'],
            'descricao': data['descricao'],
            'data_aceite': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'data_update': None,
            'aceite': data['aceite'],
            'versao': data['versao']
        }    

        resultado = users_collection.update_one(
            {'_id': dataUser['_id']},
            {'$push': {'termos': dataUserTerm}}
        )

        if resultado.matched_count == 0:
            return jsonify({'error': 'Usuário não encontrado.'}), 404

        return jsonify({'message': 'Termo adicionado com sucesso!'}), 200    
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Rota para alterar um termo do usuario
@user_term.route('/<user_cpf_cnpj>/updateUserTerm', methods=['PUT'])
def update_user_term(user_cpf_cnpj):
    try:
        data = request.get_json(force=True)

        dataUser = users_collection.find_one({'cpf_cnpj': user_cpf_cnpj})
        if not dataUser:
            return jsonify({'error': 'Usuario não encontrado!'}), 400
        
        termo_nome = data.get('nome_termo')
        if not termo_nome:
            return jsonify({'error': 'Nome do termo é obrigatório!'}), 400
        
        versao_termo = data.get('versao')
        if not versao_termo:
            return jsonify({'error': 'Versao do termo é obrigatório!'}), 400
        
        update_fields = {}

        if data['aceite']:
            update_fields['termos.$.aceite'] = data['aceite']
            update_fields['termos.$.data_aceite'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            update_fields['termos.$.data_update'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        else:
            update_fields['termos.$.aceite'] = data['aceite']
            update_fields['termos.$.data_update'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        if not update_fields:
            return jsonify({'error': 'Nenhum campo para atualizar.'}), 400
        

        result = users_collection.update_one(
            {'_id': dataUser['_id'], 'termos.nome_termo': termo_nome, 'termos.versao':versao_termo}, 
            {'$set': update_fields}
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Não foi possível atualizar o termo!'}), 500

        return jsonify({'message': 'Termo atualizado com sucesso!'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
