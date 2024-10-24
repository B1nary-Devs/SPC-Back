from flask import Blueprint, request, jsonify
from datetime import datetime
from models.app import mongo
from models.utils.sql import insertSql


term = Blueprint('term', __name__) # Rota utilizada para acesso '/terms'
terms_collection = mongo.db.termo # colecao de termos do mongo db
users_collection = mongo.db.usuario #colecao de usuarios do mongo db
@term.route('/', methods=['GET'])
def hello():
    try:
        insertSql()
        return 'Hello World!'
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para criar um termo
@term.route('/createTerm', methods=['POST'])
def create_term():
    try:
        data = request.get_json(force=True)

        required_fields = ['descricao', 'nome_termo', 'prioridade']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'O campo {field} é obrigatório!'}), 400


        nome_termo = data['nome_termo'].lower()

        terms_item = data.get('termo_item', [])

        existing_term = terms_collection.find_one(
            {'nome_termo': nome_termo},
            sort=[('versao', -1)]  # Ordenar por versão decrescente
        )
        if existing_term:
            versionTerm = round(existing_term['versao'] + 0.1, 1)
            existing_term_itens = existing_term.get('termo_item', [])

            # Dicionário para armazenar as versões dos termos existentes
            existing_item_versions = {item['termo_item_nome']: item['termo_item_versao'] for item in
                                      existing_term_itens}

            for item in terms_item:
                item_nome = item['termo_item_nome']

                # Verifique se o nome do item existe nos itens do termo existente
                if item_nome in existing_item_versions:
                    versionTermItem = round(existing_item_versions[item_nome] + 0.1, 1)
                else:
                    versionTermItem = 1.0

                item['termo_item_versao'] = versionTermItem
        else:

            versionTerm = 1.0

            # Criar o novo termo

        dataTerm = {
            'nome_termo': nome_termo,
            'descricao': data['descricao'],
            'prioridade': data['prioridade'],
            'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'versao': versionTerm,
            'termo_item': [
                {
                    "termo_item_nome": x['termo_item_nome'],
                    "termo_item_descricao": x['termo_item_descricao'],
                    "termo_item_data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "termo_item_prioridade": 2,

                    "termo_item_versao": x['termo_item_versao']
                } for x in terms_item
            ]
        }

        # Inserir o novo termo no banco
        insert = terms_collection.insert_one(dataTerm)
        result = terms_collection.find_one({'_id': insert.inserted_id})
        result['_id'] = str(result['_id'])

        # Agora, vamos atualizar todos os usuários
        usuarios = users_collection.find({})

        for usuario in usuarios:
            # Capturar o termo atual do usuário
            termo_atual = usuario.get('termo_atual', {})

            if termo_atual:
                # Mover o termo atual para o log
                dataLogTermAtual = {
                    'termo_log_nome': termo_atual.get('termo_nome'),
                    'termo_log_aceite': termo_atual.get('termo_aceite'),
                    'termo_log_versao': termo_atual.get('termo_versao'),
                    'termo_log_item_update_data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'termo_log_itens': termo_atual.get('termo_item', []),
                }
                # Atualizar o log de termos do usuário
                users_collection.update_one(
                    {'_id': usuario['_id']},
                    {'$push': {'termo_log': dataLogTermAtual}}
                )

            # Preparar o novo termo_atual com todos os itens de aceite em `false`
            novo_termo_atual = {
                "termo_nome": result['nome_termo'],
                "termo_aceite": False,
                "termo_versao": result['versao'],
                "termo_item": [
                    {
                        "termo_item_nome": item['termo_item_nome'],
                        "termo_item_aceite": False,  # Todos os itens opcionais com aceite como false
                        "termo_item_data_aceite": None  # Data de aceite será nula até que o usuário aceite
                    } for item in result['termo_item']
                ]
            }

            # Atualizar o termo_atual do usuário
            users_collection.update_one(
                {'_id': usuario['_id']},
                {'$set': {'termo_atual': novo_termo_atual}}
            )

        return jsonify({
            'Termo inserido e usuários atualizados com o novo termo': result
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para retornar todos os termos '/terms'
@term.route('/terms', methods=['GET'])
def terms_required():
    try:
        terms = list(terms_collection.find())

        terms_json = [{**term, '_id': str(term['_id'])} for term in terms]

        return jsonify(terms_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Rota para retornar os termos com o nome e se filtrar se for passado a versão '/<nome_termo>?versao=1.0'
@term.route('/<nome_termo>', methods=['GET'])
def terms_version(nome_termo):
    try:
        nome_termo = nome_termo.lower()
        versao = request.args.get('versao', type=float)
        
        if versao:
            terms = list(terms_collection.find({'nome_termo': nome_termo, 'versao': versao}))
            if not terms:
                return jsonify({'error': f'Termo e Condicoes "{nome_termo}" com a versao {versao} não foi encontrado!'}), 400
        else:
            terms = list(terms_collection.find({'nome_termo': nome_termo}))
            if not terms:
                return jsonify({'error': f'Termo e Condicoes "{nome_termo}" não foi encontrado!'}), 400
        
        terms_json = [{**term, '_id': str(term['_id'])} for term in terms]  

        return jsonify(terms_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@term.route('/latestTerm', methods=['GET'])
def latest_term():
    try:
        terms = list(terms_collection.aggregate([
            # Primeiro, ordena pelos nomes de termos e depois pelas versões em ordem decrescente
            {'$sort': {'nome_termo': 1, 'versao': -1}},  
            {
                "$group": {
                    "_id": "$nome_termo",
                    "descricao": {"$first": "$descricao"},
                    "prioridade": {"$first": "$prioridade"},
                    "versao": {"$first": "$versao"},  # Pega a versão mais recente
                    "data_cadastro": {"$first": "$data_cadastro"},
                    "termo_item": {"$first": "$termo_item"}  # Pega os itens do termo mais recente
                }
            }
        ]))

        terms_json = [{**term, '_id': str(term['_id'])} for term in terms]  

        return jsonify(terms_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@term.route('/ultimoTermo', methods=['GET'])
def ultimo_termo1():
    try:
        # Buscar todos os termos da coleção
        termos = list(terms_collection.find({}))

        # Verificar se algum termo foi encontrado
        if len(termos) == 0:
            return jsonify({'error': 'Nenhum termo encontrado.'}), 404

        # Inicializar as variáveis para armazenar o termo mais recente e sua data
        termo_mais_recente = None
        data_mais_recente = None

        # Iterar sobre todos os termos e comparar as datas
        for termo in termos:
            # Converte a string de 'data_cadastro' em datetime para comparação
            data_cadastro = datetime.strptime(termo['data_cadastro'], '%d/%m/%Y %H:%M:%S')

            # Verifica se o termo atual é mais recente
            if data_mais_recente is None or data_cadastro > data_mais_recente:
                data_mais_recente = data_cadastro
                termo_mais_recente = termo

        if termo_mais_recente:
            termo_mais_recente['_id'] = str(termo_mais_recente['_id'])  # Converte o ID para string para serialização JSON
            return jsonify(termo_mais_recente), 200

        return jsonify({'error': 'Nenhum termo encontrado.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def buscar_ultimo_termo():
    try:
        # Buscar todos os termos da coleção
        termos = list(terms_collection.find({}))

        # Verificar se algum termo foi encontrado
        if len(termos) == 0:
            return None

        # Inicializar as variáveis para armazenar o termo mais recente e sua data
        termo_mais_recente = None
        data_mais_recente = None

        # Iterar sobre todos os termos e comparar as datas
        for termo in termos:
            # Converte a string de 'data_cadastro' em datetime para comparação
            data_cadastro = datetime.strptime(termo['data_cadastro'], '%d/%m/%Y %H:%M:%S')

            # Verifica se o termo atual é mais recente
            if data_mais_recente is None or data_cadastro > data_mais_recente:
                data_mais_recente = data_cadastro
                termo_mais_recente = termo

        if termo_mais_recente:
            termo_mais_recente['_id'] = str(termo_mais_recente['_id'])  # Converte o ID para string para serialização JSON
            return termo_mais_recente

        return None
    except Exception as e:
        return None

