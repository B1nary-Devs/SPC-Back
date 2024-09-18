from flask import Blueprint, request, jsonify
from datetime import datetime
from models.app import mongo


term = Blueprint('term', __name__) # Rota utilizada para acesso '/terms'
terms_collection = mongo.db.termo # colecao de termos do mongo db


@term.route('/', methods=['GET'])
def hello():
    return "Hello World!"


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
        
        
        existing_term = terms_collection.find_one(
            {'nome_termo': nome_termo},
            sort=[('versao', -1)]  # Ordenar por versão decrescente
        )
        if existing_term:
            versionTerm = round(existing_term['versao'] + 0.1, 1)
        else:
            versionTerm = 1.0    
        
        dataTerm = {
            'nome_termo': nome_termo,
            'descricao': data['descricao'],
            'prioridade': data['prioridade'],
            'data_cadastro': datetime.now().timestamp(),
            'versao': versionTerm
        }

        result = terms_collection.insert_one(dataTerm)      
        return jsonify({'message': 'Termo e Condicoes criado com sucesso!', 'term_id': str(result.inserted_id), **result }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para retornar todos os termos ou retorna com filtro de prioridade caso seja passado na rota '/terms?prioridade=1'
@term.route('/terms', methods=['GET'])
def terms_required():
    try:
        prioridade = request.args.get('prioridade', type=int)
        if prioridade:
            terms = list(terms_collection.find({'prioridade': prioridade}))
            if not terms:
                return jsonify({'error': f'Termo e Condicoes com prioridade: {prioridade} não encontrado!'}), 404
        else:
            terms = list(terms_collection.find())

        terms_json = [{**term, '_id': str(term['_id'])} for term in terms]

        return jsonify(terms_json), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Rota para retornar os termos com o nome e se filtrar se for passado a versão '/<nome_termo>?versao=1.0'
@term.route('/<nome_termo>', methods=['GET'])
def terms_not_required(nome_termo, versao):
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
    

# Rota para retornar os termos sem repeticao e com a versao mais atualizada
@term.route('/latestTerm', methods=['GET'])
def latest_term():
    try:        
        pipeline = [
            {"$sort": {"nome_termo": 1, "versao": -1}},  
            {
                "$group": {
                    "_id": "$_id",
                    "descricao": {"$first": "$descricao"},
                    "nome_termo": {"$first": "$nome_termo"},
                    "prioridade": {"$first": "$prioridade"},
                    "versao": {"$first": "$versao"},
                    "data_cadastro": {"$first": "$data_cadastro"}
                }
            }
        ]

        terms = list(terms_collection.aggregate(pipeline))

        return jsonify(terms), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

