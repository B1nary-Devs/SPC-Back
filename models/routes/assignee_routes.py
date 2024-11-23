from flask import Blueprint, request, jsonify
from bson import ObjectId
from models.app import mongo
from models.routes.user_routes import users_collection
from datetime import datetime
from flask import jsonify

# Inicialização das coleções do MongoDB
duplicata_collection = mongo.db.duplicatas
assignee = Blueprint('assignee', __name__)
assignee_collection = mongo.db.assigne


# Rota para criação de usuários com validação de termos
@assignee.route('/createAssignee', methods=['POST'])
def create_assignee():
    try:
        data = request.get_json(force=True)

        # Extrai dados gerais da cessionária
        cessionaria_cnpj = data.get('cessionaria_cnpj')

        # Verifica se o CNPJ já existe na coleção de cessionárias
        cessionaria_exists = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})
        if cessionaria_exists:
            return jsonify({'error': f'Cessionária com CNPJ {cessionaria_cnpj} já existe'}), 400

        # Inicializa o dicionário da cessionária
        dataCessionaria = {
            'cessionaria_nome': data['cessionaria_nome'],
            'cessionaria_cnpj': cessionaria_cnpj,
            'cessionaria_score': data.get('cessionaria_score'),
            'cessionaria_sacado': []
        }

        # Se existir sacados fornecidos, adiciona à lista de sacados
        if 'cessionaria_sacado' in data and isinstance(data['cessionaria_sacado'], list):
            for sacado in data['cessionaria_sacado']:
                try:
                    # Converte as datas para strings no formato 'YYYY-MM-DD' para evitar problemas com o MongoDB
                    duplicada_data_inicial = sacado.get('cessionaria_sacado_duplicadas_data_inicial')
                    duplicada_data_final = sacado.get('cessionaria_sacado_duplicadas_data_final')
                    data_pagamento = sacado.get('cessionaria_sacado_data_pagamento')

                    duplicadas_valor = sacado.get('cessionaria_sacado_duplicadas_valor')

                    # Verifica se o valor da duplicata está presente
                    #if duplicadas_valor is None:
                    #    return jsonify({'error': 'Valor da duplicata não fornecido para um sacado'}), 400

                    # Busca duplicatas existentes para o mesmo sacado
                    cessionaria_sacado_cnpj = sacado.get('cessionaria_sacado_cnpj')
                    if not cessionaria_sacado_cnpj:
                        return jsonify({'error': 'CNPJ do sacado não fornecido'}), 400

                    duplicatas_sacado = [
                        s.get('cessionaria_sacado_duplicadas_valor')
                        for cessionaria in assignee_collection.find({})
                        for s in cessionaria.get('cessionaria_sacado', [])
                        if s.get('cessionaria_sacado_cnpj') == cessionaria_sacado_cnpj
                    ]

                    # Remove valores nulos ou inválidos
                    duplicatas_sacado = [valor for valor in duplicatas_sacado if isinstance(valor, (int, float))]

                    # Calcula a média dos valores históricos e verifica fraude
                    is_fraude = False
                    if duplicatas_sacado:
                        media_valores = sum(duplicatas_sacado) / len(duplicatas_sacado)
                        limite_inferior = media_valores * 0.8
                        limite_superior = media_valores * 1.2
                        is_fraude = not (limite_inferior <= duplicadas_valor <= limite_superior)

                    # Cria o dicionário do sacado
                    sacado_data = {
                        'cessionaria_sacado_id': sacado['cessionaria_sacado_id'],
                        'cessionaria_sacado_cnpj': str(sacado['cessionaria_sacado_cnpj']),
                        'cessionaria_sacado_score': sacado['cessionaria_sacado_score'],
                        'cessionaria_sacado_duplicadas_data_inicial': duplicada_data_inicial,
                        'cessionaria_sacado_duplicadas_data_final': duplicada_data_final,
                        'cessionaria_sacado_duplicata_status': sacado['cessionaria_sacado_duplicata_status'],
                        'cessionaria_sacado_nome': sacado['cessionaria_sacado_nome'],
                        'cessionaria_sacado_contato': sacado.get('cessionaria_sacado_contato'),
                        'cessionaria_sacado_email': sacado.get('cessionaria_sacado_email'),
                        'cessionaria_sacado_data_pagamento': data_pagamento,
                        'cessionaria_sacado_duplicadas_valor': sacado['cessionaria_sacado_duplicadas_valor'],
                        'cessionaria_sacado_chance_fraude': is_fraude


                    }

                    dataCessionaria['cessionaria_sacado'].append(sacado_data)

                except Exception as e:
                    # Log para identificar problemas específicos com o sacado
                    return jsonify({'error': f'Erro ao processar sacado: {str(e)}', 'sacado': sacado}), 400

        # Insere a cessionária na coleção
        assignee_collection.insert_one(dataCessionaria)

        return jsonify({'message': 'Cessionária criada com sucesso!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@assignee.route('/listAssignees', methods=['GET'])
def list_assignees():
    try:
        cessionarias = assignee_collection.find({})
        cessionarias_json = [{**cessionaria, '_id': str(cessionaria['_id'])} for cessionaria in cessionarias]

        assignee_list = []
        for cessionaria in cessionarias_json:
            # Verifica se cessionaria_sacado existe e é uma lista
            cessionaria_sacado = cessionaria.get('cessionaria_sacado', None)

            if isinstance(cessionaria_sacado, list) and cessionaria_sacado:
                cessionaria['cessionaria_sacado'] = cessionaria_sacado
            else:
                cessionaria['cessionaria_sacado'] = None  # Caso não seja uma lista ou esteja vazia

            assignee_list.append(cessionaria)

        return jsonify(assignee_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>', methods=['GET'])
def one_assignee(cessionaria_cnpj):
    try:
        # Busca a cessionária com base no CNPJ fornecido
        dataAssignee = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})

        if not dataAssignee:
            return jsonify({'error': 'Cessionária não encontrada!'}), 404

        # Converte o campo _id para string
        dataAssignee['_id'] = str(dataAssignee['_id'])

        # Extrai o subdocumento de cessionaria_sacado
        cessionaria_sacado = dataAssignee.get('cessionaria_sacado', [])

        # Garante que cessionaria_sacado seja uma lista de sacados
        if isinstance(cessionaria_sacado, dict):
            # Se for um dicionário, transforma em uma lista contendo esse único dicionário
            dataAssignee['cessionaria_sacado'] = [cessionaria_sacado]
        elif isinstance(cessionaria_sacado, list):
            # Se já for uma lista, mantemos os dados como estão
            dataAssignee['cessionaria_sacado'] = cessionaria_sacado
        else:
            # Caso contrário, inicializa como uma lista vazia
            dataAssignee['cessionaria_sacado'] = []

        return jsonify(dataAssignee), 200  # Retorna diretamente o objeto cessionário

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>/updateAssignee', methods=['PUT'])
def update_assignee(cessionaria_cnpj):
    try:
        data = request.get_json(force=True)

        # Busca a cessionária com base no CNPJ fornecido
        dataAssignee = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})

        if not dataAssignee:
            return jsonify({'error': 'Cessionária não encontrada!'}), 400

        update_fields = {}

        # Atualiza os campos da cessionária, se fornecido
        for field in ['cessionaria_nome', 'cessionaria_cnpj', 'cessionaria_score']:
            if field in data:
                update_fields[field] = data[field]

        # Atualiza os dados da cessionária
        if update_fields:
            assignee_collection.update_one({'cessionaria_cnpj': cessionaria_cnpj}, {'$set': update_fields})

        # Verifica se há um novo sacado a ser adicionado
        if 'cessionaria_sacado' in data:
            new_sacado = data['cessionaria_sacado']
            sacado_id = new_sacado.get('cessionaria_sacado_id')

            # Verifica se o sacado já existe na lista de sacados
            sacado_exists = assignee_collection.find_one({
                'cessionaria_cnpj': cessionaria_cnpj,
                'cessionaria_sacado.cessionaria_sacado_id': sacado_id
            })

            if sacado_exists:
                # Atualiza o sacado existente usando o operador posicional $
                update_sacado_fields = {f'cessionaria_sacado.$.{key}': new_sacado.get(key) for key in [
                    'cessionaria_sacado_score', 'cessionaria_sacado_duplicadas_data_inicial',
                    'cessionaria_sacado_duplicadas_data_final', 'cessionaria_sacado_duplicata_status',
                    'cessionaria_sacado_nome', 'cessionaria_sacado_empresa',
                    'cessionaria_sacado_contato', 'cessionaria_sacado_email',
                    'cessionaria_sacado_data_pagamento', 'cessionaria_sacado_duplicadas_valor',
                    'cessionaria_sacado_chance_fraude']}

                assignee_collection.update_one(
                    {'cessionaria_cnpj': cessionaria_cnpj, 'cessionaria_sacado.cessionaria_sacado_id': sacado_id},
                    {'$set': update_sacado_fields}
                )
            else:
                # Adiciona um novo sacado à lista usando $push
                new_sacado_data = {
                    'cessionaria_sacado_id': sacado_id,
                    'cessionaria_sacado_score': new_sacado.get('cessionaria_sacado_score'),
                    'cessionaria_sacado_duplicadas_data_inicial': new_sacado.get('cessionaria_sacado_duplicadas_data_inicial'),
                    'cessionaria_sacado_duplicadas_data_final': new_sacado.get('cessionaria_sacado_duplicadas_data_final'),
                    'cessionaria_sacado_duplicata_status': new_sacado.get('cessionaria_sacado_duplicata_status'),
                    'cessionaria_sacado_nome': new_sacado.get('cessionaria_sacado_nome'),
                    'cessionaria_sacado_empresa': new_sacado.get('cessionaria_sacado_empresa'),
                    'cessionaria_sacado_contato': new_sacado.get('cessionaria_sacado_contato'),
                    'cessionaria_sacado_email': new_sacado.get('cessionaria_sacado_email'),
                    'cessionaria_sacado_data_pagamento': new_sacado.get('cessionaria_sacado_data_pagamento'),
                    'cessionaria_sacado_duplicadas_valor': new_sacado.get('cessionaria_sacado_duplicadas_valor'),
                    'cessionaria_sacado_chance_fraude': new_sacado.get('cessionaria_sacado_chance_fraude')
                }

                assignee_collection.update_one(
                    {'cessionaria_cnpj': cessionaria_cnpj},
                    {'$push': {'cessionaria_sacado': new_sacado_data}}
                )

        return jsonify({'message': 'Cessionária e sacado atualizados com sucesso!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>/duplicatas/<status>', methods=['GET'])
def get_duplicatas_by_cnpj_and_status(cessionaria_cnpj, status):
    valid_status = ["Finalizado", "Vencido", "A vencer"]

    # Verifica se o status informado é válido
    if status not in valid_status:
        return jsonify({"message": "Status inválido"}), 400

    # Busca a cessionária pelo CNPJ
    cessionaria = assignee_collection.find_one({"cessionaria_cnpj": cessionaria_cnpj})

    if not cessionaria:
        return jsonify({"message": "Cessionária não encontrada"}), 404

    # Converte o ObjectId para string para evitar erros de serialização
    cessionaria["_id"] = str(cessionaria["_id"])

    # Filtra os sacados da cessionária pelo status solicitado
    data_atual = datetime.now()
    sacados_filtrados = []

    if isinstance(cessionaria.get('cessionaria_sacado', []), list):
        for sacado in cessionaria['cessionaria_sacado']:
            # Atualiza o status da duplicata de acordo com a data
            duplicata_data_inicial = sacado.get('cessionaria_sacado_duplicadas_data_inicial')
            duplicata_data_final = sacado.get('cessionaria_sacado_duplicadas_data_final')

            if duplicata_data_final:
                duplicata_data_final = datetime.fromtimestamp(duplicata_data_final)
                if duplicata_data_final < data_atual:
                    sacado['cessionaria_sacado_duplicata_status'] = "Vencido"
                else:
                    sacado['cessionaria_sacado_duplicata_status'] = "A vencer"

            # Adiciona o sacado à lista se o status for o desejado
            if sacado.get('cessionaria_sacado_duplicata_status') == status:
                sacados_filtrados.append(sacado)

    # Retorna todos os dados da cessionária, incluindo somente os sacados com o status desejado
    cessionaria['cessionaria_sacado'] = sacados_filtrados

    return jsonify(cessionaria), 200

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


# @assignee.route('/<cessionaria_cnpj>/loc', methods=['GET'])
# def get_loc_assignee(cessionaria_cnpj):
#     try:
#         # Busca a cessionária com base no CNPJ fornecido
#         cessionaria = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})
#
#         if not cessionaria:
#             return jsonify({'error': 'Cessionária não encontrada!'}), 404
#
#         # Converte o campo _id para string
#         cessionaria['_id'] = str(cessionaria['_id'])
#
#         # Filtra os dados de `cessionaria_sacado` para manter apenas `estado`, `lagitude`, e `longitude`
#         sacados_simplified = []
#         for sacado in cessionaria.get('cessionaria_sacado', []):
#             sacado_simplificado = {
#                 'cessionaria_sacado_estado': sacado.get('cessionaria_sacado_estado'),
#                 'cessionaria_sacado_lagitude': sacado.get('cessionaria_sacado_lagitude'),
#                 'cessionaria_sacado_longitude': sacado.get('cessionaria_sacado_longitude')
#             }
#             sacados_simplified.append(sacado_simplificado)
#
#         # Substitui a lista original de `cessionaria_sacado` pela versão simplificada
#         cessionaria['cessionaria_sacado'] = sacados_simplified
#
#         return jsonify(cessionaria), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@assignee.route('/<cessionaria_cnpj>/fraudulent_sacados', methods=['GET'])
def get_assignee_with_fraudulent_sacados(cessionaria_cnpj):
    try:
        # Busca a cessionária com base no CNPJ fornecido
        cessionaria = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})

        if not cessionaria:
            return jsonify({'error': 'Cessionária não encontrada!'}), 404

        # Converte o campo _id para string
        cessionaria['_id'] = str(cessionaria['_id'])

        # Filtra a lista de sacados para manter apenas aqueles com chance de fraude True
        sacados_fraudulentos = [
            sacado for sacado in cessionaria.get('cessionaria_sacado', [])
            if sacado.get('cessionaria_sacado_chance_fraude') == True
        ]

        # Substitui a lista original de `cessionaria_sacado` pela lista filtrada
        cessionaria['cessionaria_sacado'] = sacados_fraudulentos

        return jsonify(cessionaria), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assignee.route('/fraudulent_assignees', methods=['GET'])
def get_fraudulent_assignees():
    try:
        # Busca todas as cessionárias na coleção
        cessionarias = assignee_collection.find({})

        fraudulent_assignees = []

        # Filtra as cessionárias com sacados fraudulentos
        for cessionaria in cessionarias:
            sacados_fraudulentos = [
                sacado for sacado in cessionaria.get('cessionaria_sacado', [])
                if sacado.get('cessionaria_sacado_chance_fraude') == True
            ]

            # Adiciona à lista somente se houver sacados fraudulentos
            if sacados_fraudulentos:
                fraudulent_assignees.append({
                    'cessionaria_nome': cessionaria.get('cessionaria_nome'),
                    'cessionaria_cnpj': cessionaria.get('cessionaria_cnpj')
                })

        return jsonify(fraudulent_assignees), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

