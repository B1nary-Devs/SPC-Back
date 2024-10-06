from flask import Blueprint, request, jsonify
from datetime import datetime
from models.app import mongo


user_term = Blueprint('user_term', __name__)# Rota utilizada para acesso '/user_terms'
users_collection = mongo.db.usuario # colecao de termos do mongo db


# Rota para atualizar o termo atual obrigatorio
@user_term.route('/<user_cpf_cnpj>/updateUserTerm', methods=['POST'])
def update_user_terms(user_cpf_cnpj):
    try:
        data = request.get_json(force=True)

        dataUser = users_collection.find_one({'cpf_cnpj': user_cpf_cnpj})
        if not dataUser:
            return jsonify({'error': 'Usuario não encontrado!'}), 400
        
        # Captura o termo_atual
        term_atual = dataUser.get('termo_atual', {})

        # Inserir no log termo
        dataLogTermAtual = {
            'termo_log_nome': term_atual.get('termo_nome'),
            'termo_log_aceite': term_atual.get('termo_aceite'),
            'termo_log_versao': term_atual.get('termo_versao'),
            "termo_log_item_update_data": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'termo_log_itens': term_atual.get('termo_item', []),
        }
        
        users_collection.update_one(
            {'_id': dataUser['_id']},
            {'$push': {'termo_log': dataLogTermAtual}}
        )

        # Atualizar o termo_atual com os dados do JSON passado
        term_itens = data.get('termo_atual', {}).get('termo_item', [])

        # Montando o novo termo
        dataUserTerm = {
            "termo_nome": data.get('termo_nome'),  
            "termo_aceite": data.get('termo_aceite'),
            "termo_versao": data.get('termo_versao'),
            "termo_item": [
                {
                    "termo_item_nome": item.get('termo_item_nome'),
                    "termo_item_aceite": item.get('termo_item_aceite'),
                    "termo_item_data_aceite": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                } for item in term_itens 
            ]  
        }    

        resultado = users_collection.update_one(
            {'_id': dataUser['_id']},
            {'$set': {'termo_atual': dataUserTerm}}
        )

        if resultado.matched_count == 0:
            return jsonify({'error': 'Usuário não encontrado.'}), 404

        return jsonify({'message': 'Termo adicionado com sucesso!'}), 200    
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


# Rota para atualizar o aceite dos itens
@user_term.route('/<user_cpf_cnpj>/updateUserTermItens', methods=['PUT'])
def update_user_term_itens(user_cpf_cnpj):
    try:
        data = request.get_json(force=True)

        dataUser = users_collection.find_one({'cpf_cnpj': user_cpf_cnpj})
        if not dataUser:
            return jsonify({'error': 'Usuario não encontrado!'}), 400
        
        term_atual = dataUser.get('termo_atual', {})
        term_nome = term_atual.get('termo_nome', '')

        # Log para os itens que foram modificados
        dataLog = []
        term_itens = term_atual.get('termo_item', [])

        for item in term_itens:
            # Verifica se o item tem um novo estado (aceite) passado no JSON
            novo_aceite = next((i['termo_item_aceite'] for i in data['termo_item'] if i['termo_item_nome'] == item['termo_item_nome']), None)
            if novo_aceite is not None and item['termo_item_aceite'] != novo_aceite:
                # Adiciona ao log
                dataLog.append({
                    'termo_log_nome': term_nome,
                    'termo_log_item_nome': item['termo_item_nome'],
                    'termo_log_item_aceite': novo_aceite,
                    'termo_log_item_update_data': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                })
                # Atualiza o item no banco de dados
                item['termo_item_aceite'] = novo_aceite

        # Atualiza os termo_item no banco de dados
        resultado = users_collection.update_one(
            {'_id': dataUser['_id']},
            {'$set': {'termo_atual.termo_item': term_itens}}
        )

        # Atualiza o log se houver itens modificados
        if dataLog:
            users_collection.update_one(
                {'_id': dataUser['_id']},
                {'$push': {'termo_log': {'$each': dataLog}}}
            )

        if resultado.matched_count == 0:
            return jsonify({'error': 'Usuário não encontrado.'}), 404

        return jsonify({'message': 'Termos atualizados com sucesso!'}), 200    

    except Exception as e:
        return jsonify({'error': str(e)}), 500
