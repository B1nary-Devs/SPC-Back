from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash
from models.app import mongo


user = Blueprint('user', __name__) #Rota utilizada para acesso '/users'
users_collection = mongo.db.usuario #colecao de usuarios do mongo db


# Rota para criação de usuarios com validacao de termos
@user.route('/createUser', methods=['POST'])
def create_user():
    try:
        data = request.get_json(force=True)
        password_hash = generate_password_hash(data['senha'])
        user_termos = data.get('termos', [])

        if not user_termos:
            return jsonify({'error': 'Nenhum termo obrigatorio foi aceito pelo usuário.'}), 400
        
        userExists = users_collection.find_one({'cpf_cnpj': data['cpf_cnpj']})
        if userExists:
            return jsonify({'error': f'O usuario com cpf/cnpj: {userExists["cpf_cnpj"]} ja existe'}), 400
        
        required_fields = ['nome', 'email', 'cpf_cnpj', 'cep', 'endereco', 'senha']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'O campo {field} é obrigatório!'}), 400

        dataUser = {
            'nome': data['nome'],
            'email': data['email'],
            'cpf_cnpj': data['cpf_cnpj'],
            'telefone': data['telefone'],
            'celular': data['celular'],
            'cep': data['cep'],
            'endereco': data['endereco'],
            'senha': password_hash,
            'termos': [{
                'nome_termo': x['nome_termo'],
                'prioridade': x['prioridade'],
                'descricao': x['descricao'],
                'data_aceite': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'data_update': None,
                'aceite': x['aceite'],
                'versao': x['versao']
            } for x in user_termos]
        }

        insert = users_collection.insert_one(dataUser)
        result = users_collection.find_one({'_id': insert.inserted_id}) 
        result['_id'] = str(result['_id'])
        
        return jsonify({
            'Usuario inserido': result
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Rota para retorno de lista usuarios
@user.route('/usersList', methods=['GET'])
def list_users():
    try:
        usuarios = list(users_collection.find({}))
        usuarios_json = [{**usuario, '_id': str(usuario['_id'])} for usuario in usuarios]

        return jsonify(usuarios_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para retorno de um usuario
@user.route('/<usuario_cpf_cnpj>', methods=['GET'])
def oneUser(usuario_cpf_cnpj):
    try:
        dataUser = users_collection.find_one({'cpf_cnpj': usuario_cpf_cnpj})
        if not dataUser:
            return jsonify({'error': 'Usuario não encontrado!'}), 400
        
        dataUser['_id'] = str(dataUser['_id']) 

        return jsonify(dataUser), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para update de usuario
@user.route('/<usuario_cpf_cnpj>/updateUser', methods=['PUT'])
def updateUser(usuario_cpf_cnpj):
    try:
        data = request.get_json(force=True)
        dataUser = users_collection.find_one({'cpf_cnpj': usuario_cpf_cnpj})

        if not dataUser:
            return jsonify({'error': 'Usuario não encontrado!'}), 400
        
        update_fields = {}

        if 'nome' in data:
            update_fields['nome'] = data['nome']
        if 'email' in data:
            update_fields['email'] = data['email']
        if 'cpf_cnpj' in data:
            update_fields['cpf_cnpj'] = data['cpf_cnpj']
        if 'telefone' in data:
            update_fields['telefone'] = data['telefone']
        if 'celular' in data:
            update_fields['celular'] = data['celular']
        if 'cep' in data:
            update_fields['cep'] = data['cep']
        if 'endereco' in data:
            update_fields['endereco'] = data['endereco']
        if 'senha' in data:
            password_hash = generate_password_hash(data['senha'])
            update_fields['senha'] = password_hash

        if not update_fields:
            return jsonify({'error': 'Nenhum campo para atualizar.'}), 400
        
        result = users_collection.update_one({'cpf_cnpj': usuario_cpf_cnpj}, {'$set': update_fields})
        if result.matched_count == 0:
            return jsonify({'error': 'Usuário não encontrado!'}), 404
        
        return jsonify({'message': 'Usuário atualizado com sucesso!'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para deletar de usuario
@user.route('/<usuario_cpf_cnpj>/deleteUser', methods=['DELETE'])
def deleteUser(usuario_cpf_cnpj):
    try:
        dataUser = users_collection.find_one({'cpf_cnpj': usuario_cpf_cnpj})
        if not dataUser:
            return jsonify({'error': 'Usuario não encontrado!'}), 400
        
        result = users_collection.delete_one({'cpf_cnpj': usuario_cpf_cnpj})
        if result.deleted_count == 0:
            return jsonify({'error': 'Não foi possível excluir o usuário.'}), 500
        
        return jsonify({'message': 'Usuário excluído com sucesso!'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
