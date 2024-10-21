from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash
from models.app import mongo
from models.utils.email import registraEmail
from .term_routes import buscar_ultimo_termo
import os
import csv
from .salvar_email import salvar_no_google_sheets

user = Blueprint('user', __name__) #Rota utilizada para acesso '/users'
users_collection = mongo.db.usuario #colecao de usuarios do mongo db


# Rota para criação de usuarios com validacao de termos
# Supondo que a função ultimo_termo já foi importada corretamente no arquivo do usuário

@user.route('/createUser', methods=['POST'])
def create_user():
    try:
        data = request.get_json(force=True)
        password_hash = generate_password_hash(data['senha'])

        ultimo_termo = buscar_ultimo_termo()

        if not ultimo_termo:
            return jsonify({'error': 'Nenhum termo foi encontrado no sistema.'}), 400

        # Verificar se o termo possui itens válidos
        if 'termo_item' not in ultimo_termo or not ultimo_termo['termo_item']:
            return jsonify({'error': f'O último termo não contém itens válidos. aqui ->{ultimo_termo}'}), 400

        userExists = users_collection.find_one({'cpf_cnpj': data['cpf_cnpj']})
        if userExists:
            return jsonify({'error': f'O usuario com cpf/cnpj: {userExists["cpf_cnpj"]} já existe'}), 400

        required_fields = ['nome', 'email', 'cpf_cnpj', 'cep', 'endereco', 'senha']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'O campo {field} é obrigatório!'}), 400

        registraEmail(data['nome'], data['email'])

        # Inserção de usuário e termo log com o último termo obtido
        dataUser = {
            'nome': data['nome'],
            'email': data['email'],
            'senha': password_hash,
            'perfil': data['perfil'],
            'cpf_cnpj': data['cpf_cnpj'],
            'telefone': data['telefone'],
            'celular': data['celular'],
            'cep': data['cep'],
            'endereco': data['endereco'],
            'termo_atual': {
                'termo_nome': ultimo_termo['nome_termo'],
                'termo_aceite': False,  # Não aceito ainda
                'termo_versao': ultimo_termo['versao'],
                'termo_item': [
                    {
                        'termo_item_nome': x['termo_item_nome'],
                        'termo_item_aceite': False,  # Não aceito ainda
                        'termo_item_data_aceite': None,  # Data de aceite será None até que o usuário aceite
                        'termo_item_data_cadastro': x['termo_item_data_cadastro']  # Data de cadastro do item original
                    } for x in ultimo_termo['termo_item']
                ]
            },
            'termo_log': []  # O termo log está vazio porque é um novo usuário
        }

        # Insere o usuário no MongoDB
        insert = users_collection.insert_one(dataUser)
        result = users_collection.find_one({'_id': insert.inserted_id})
        result['_id'] = str(result['_id'])

        # Escrever a linha com o nome e email
        salvar_no_google_sheets(data['nome'],data['email'])

        # Retorna o usuário inserido
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

#akaka
# Rota para atualizar informações do usuário e termo
@user.route('/<user_cpf_cnpj>/update', methods=['PUT'])
def update_user_and_term(user_cpf_cnpj):
    try:
        data = request.get_json(force=True)

        # Buscar o usuário pelo CPF/CNPJ
        dataUser = users_collection.find_one({'cpf_cnpj': user_cpf_cnpj})
        if not dataUser:
            return jsonify({'error': 'Usuário não encontrado!'}), 400

        # Inicializar o dicionário de campos a serem atualizados
        update_fields = {}

        # Atualizar informações gerais do usuário (nome, email, etc.)
        if 'nome' in data:
            update_fields['nome'] = data['nome']
        if 'email' in data:
            update_fields['email'] = data['email']
        if 'telefone' in data:
            update_fields['telefone'] = data['telefone']
        if 'celular' in data:
            update_fields['celular'] = data['celular']
        if 'cep' in data:
            update_fields['cep'] = data['cep']
        if 'endereco' in data:
            update_fields['endereco'] = data['endereco']
        if 'senha' in data:
            # Se a senha for alterada, gerar o hash da nova senha
            password_hash = generate_password_hash(data['senha'])
            update_fields['senha'] = password_hash

        # Captura o termo_atual do usuário
        term_atual = dataUser.get('termo_atual', {})

        # Verificar se o termo foi alterado
        novo_termo = data.get('termo_atual', {})

        # Comparação dos campos principais (nome, versão, aceite)
        termo_diferente = (
            term_atual.get('termo_nome') != novo_termo.get('termo_nome') or
            term_atual.get('termo_versao') != novo_termo.get('termo_versao') or
            term_atual.get('termo_aceite') != novo_termo.get('termo_aceite')
        )

        # Verificar mudanças nos itens do termo
        termo_itens_diferentes = False
        itens_atuais = term_atual.get('termo_item', [])
        itens_novos = novo_termo.get('termo_item', [])

        # Se o número de itens for diferente, já podemos considerar uma mudança
        if len(itens_atuais) != len(itens_novos):
            termo_itens_diferentes = True
        else:
            # Comparar os itens um por um
            for item_atual, item_novo in zip(itens_atuais, itens_novos):
                if (item_atual.get('termo_item_nome') != item_novo.get('termo_item_nome') or
                    item_atual.get('termo_item_aceite') != item_novo.get('termo_item_aceite') or
                    item_atual.get('termo_item_data_aceite') != item_novo.get('termo_item_data_aceite')):
                    termo_itens_diferentes = True
                    break

        # Debugging: mostrar se os termos ou itens são diferentes
        print("Termo Diferente:", termo_diferente)
        print("Itens Diferentes:", termo_itens_diferentes)

        # Se houver qualquer diferença no termo principal ou nos itens, mover o termo para o log
        if (termo_diferente or termo_itens_diferentes) and term_atual:
            # Adicionar o termo atual ao log
            dataLogTermAtual = {
                'termo_log_nome': term_atual.get('termo_nome'),
                'termo_log_aceite': term_atual.get('termo_aceite'),
                'termo_log_versao': term_atual.get('termo_versao'),
                'termo_log_item_update_data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'termo_log_itens': term_atual.get('termo_item', []),
            }

            # Empurra o termo atual para o log de termos
            users_collection.update_one(
                {'_id': dataUser['_id']},
                {'$push': {'termo_log': dataLogTermAtual}}
            )

            # Preparar o novo termo para atualizar o termo_atual
            term_itens = novo_termo.get('termo_item', [])
            update_fields['termo_atual'] = {
                "termo_nome": novo_termo.get('termo_nome'),
                "termo_aceite": novo_termo.get('termo_aceite'),
                "termo_versao": novo_termo.get('termo_versao'),
                "termo_item": [
                    {
                        "termo_item_nome": item.get('termo_item_nome'),
                        "termo_item_aceite": item.get('termo_item_aceite'),
                        "termo_item_data_aceite": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    } for item in term_itens
                ]
            }

        # Verificar se há campos a serem atualizados
        if not update_fields:
            return jsonify({'message': 'Nenhum campo para atualizar.'}), 400

        # Atualizar os campos do usuário (informações gerais e termo, se aplicável)
        resultado = users_collection.update_one(
            {'_id': dataUser['_id']},
            {'$set': update_fields}
        )

        if resultado.matched_count == 0:
            return jsonify({'error': 'Usuário não encontrado!'}), 404

        return jsonify({'message': 'Informações do usuário atualizadas com sucesso!'}), 200

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
    
