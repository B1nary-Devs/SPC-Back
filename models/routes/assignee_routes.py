from flask import Blueprint, request, jsonify
from models.app import mongo
from models.routes.user_routes import users_collection
from datetime import datetime

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

        # Verifica se o CNPJ já existe na coleção de usuários
        userExists = users_collection.find_one({'cpf_cnpj': cessionaria_cnpj})
        if not userExists:
            return jsonify({
                               'error': 'CNPJ não encontrado na base de usuários. A cessionária só pode ser criada se o CNPJ já estiver registrado como um usuário.'}), 400

        cessionariaExists = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})
        if cessionariaExists:
            return jsonify({'error': f'Cessionária com CNPJ {cessionariaExists["cessionaria_cnpj"]} já existe'}), 400

        # Inicializa o dicionário da cessionária
        dataCessionaria = {
            'cessionaria_nome': data['cessionaria_nome'],
            'cessionaria_cnpj': cessionaria_cnpj,
            'cessionaria_score': data.get('cessionaria_score', None),
            'cessionaria_sacado': data.get('cessionaria_sacado', None)  # Adiciona diretamente aqui
        }

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
            # Verifica se cessionaria_sacado é um dicionário
            cessionaria_sacado = cessionaria.get('cessionaria_sacado', {})
            if isinstance(cessionaria_sacado, dict):
                cessionaria['cessionaria_sacado'] = {
                    'cessionaria_sacado_id': cessionaria_sacado.get('cessionaria_sacado_id'),
                    'cessionaria_sacado_score': cessionaria_sacado.get('cessionaria_sacado_score'),
                    'cessionaria_sacado_duplicadas_data_inicial': cessionaria_sacado.get(
                        'cessionaria_sacado_duplicadas_data_inicial'),
                    'cessionaria_sacado_duplicadas_data_final': cessionaria_sacado.get(
                        'cessionaria_sacado_duplicadas_data_final'),
                    'cessionaria_sacado_duplicata_status': cessionaria_sacado.get(
                        'cessionaria_sacado_duplicata_status'),
                    'cessionaria_sacado_nome': cessionaria_sacado.get('cessionaria_sacado_nome'),
                    'cessionaria_sacado_empresa': cessionaria_sacado.get('cessionaria_sacado_empresa'),
                    'cessionaria_sacado_contato': cessionaria_sacado.get('cessionaria_sacado_contato'),
                    'cessionaria_sacado_email': cessionaria_sacado.get('cessionaria_sacado_email'),
                    'cessionaria_sacado_data_pagamento': cessionaria_sacado.get('cessionaria_sacado_data_pagamento')
                }
            else:
                cessionaria['cessionaria_sacado'] = None  # Caso não seja um dicionário

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
            return jsonify({'error': 'Cessionária não encontrada!'}), 400

        # Converte o campo _id para string
        dataAssignee['_id'] = str(dataAssignee['_id'])

        # Extrai o subdocumento de cessionaria_sacado
        cessionaria_sacado = dataAssignee.get('cessionaria_sacado', {})
        if isinstance(cessionaria_sacado, dict):  # Verifica se é um dicionário
            dataAssignee['cessionaria_sacado'] = {
                'cessionaria_sacado_id': cessionaria_sacado.get('cessionaria_sacado_id'),
                'cessionaria_sacado_score': cessionaria_sacado.get('cessionaria_sacado_score'),
                'cessionaria_sacado_duplicadas_data_inicial': cessionaria_sacado.get(
                    'cessionaria_sacado_duplicadas_data_inicial'),
                'cessionaria_sacado_duplicadas_data_final': cessionaria_sacado.get(
                    'cessionaria_sacado_duplicadas_data_final'),
                'cessionaria_sacado_duplicata_status': cessionaria_sacado.get('cessionaria_sacado_duplicata_status'),
                'cessionaria_sacado_nome': cessionaria_sacado.get('cessionaria_sacado_nome'),
                'cessionaria_sacado_empresa': cessionaria_sacado.get('cessionaria_sacado_empresa'),
                'cessionaria_sacado_contato': cessionaria_sacado.get('cessionaria_sacado_contato'),
                'cessionaria_sacado_email': cessionaria_sacado.get('cessionaria_sacado_email'),
                'cessionaria_sacado_data_pagamento': cessionaria_sacado.get('cessionaria_sacado_data_pagamento')
            }
        else:
            dataAssignee['cessionaria_sacado'] = None

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

            # Verifica se o sacado já existe para essa cessionária
            sacado_exists = assignee_collection.find_one({
                'cessionaria_cnpj': cessionaria_cnpj,
                'cessionaria_sacado.cessionaria_sacado_id': sacado_id
            })

            if sacado_exists:
                # Atualiza o sacado existente
                update_sacado_fields = {key: new_sacado.get(key) for key in [
                    'cessionaria_sacado_score', 'cessionaria_sacado_duplicadas_data_inicial',
                    'cessionaria_sacado_duplicadas_data_final', 'cessionaria_sacado_duplicata_status',
                    'cessionaria_sacado_nome', 'cessionaria_sacado_empresa',
                    'cessionaria_sacado_contato', 'cessionaria_sacado_email',
                    'cessionaria_sacado_data_pagamento'
                ]}
                assignee_collection.update_one(
                    {'cessionaria_cnpj': cessionaria_cnpj, 'cessionaria_sacado.cessionaria_sacado_id': sacado_id},
                    {'$set': update_sacado_fields}
                )
            else:
                # Inicializa cessionaria_sacado como um array se não existir
                existing_data = assignee_collection.find_one({'cessionaria_cnpj': cessionaria_cnpj})
                if not isinstance(existing_data.get('cessionaria_sacado', []), list):
                    assignee_collection.update_one(
                        {'cessionaria_cnpj': cessionaria_cnpj},
                        {'$set': {'cessionaria_sacado': []}}
                    )

                # Adiciona um novo sacado
                new_sacado_data = {
                    'cessionaria_sacado_id': sacado_id,
                    'cessionaria_sacado_score': new_sacado.get('cessionaria_sacado_score'),
                    'cessionaria_sacado_duplicadas_data_inicial': new_sacado.get(
                        'cessionaria_sacado_duplicadas_data_inicial'),
                    'cessionaria_sacado_duplicadas_data_final': new_sacado.get(
                        'cessionaria_sacado_duplicadas_data_final'),
                    'cessionaria_sacado_duplicata_status': new_sacado.get('cessionaria_sacado_duplicata_status'),
                    'cessionaria_sacado_nome': new_sacado.get('cessionaria_sacado_nome'),
                    'cessionaria_sacado_empresa': new_sacado.get('cessionaria_sacado_empresa'),
                    'cessionaria_sacado_contato': new_sacado.get('cessionaria_sacado_contato'),
                    'cessionaria_sacado_email': new_sacado.get('cessionaria_sacado_email'),
                    'cessionaria_sacado_data_pagamento': new_sacado.get('cessionaria_sacado_data_pagamento')
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

    # Atualiza o status das duplicatas baseado na data atual
    data_atual = datetime.now()

    if isinstance(cessionaria.get('cessionaria_sacado', {}), dict):
        duplicatas = cessionaria['cessionaria_sacado'].get('duplicatas', [])
        for duplicata in duplicatas:
            # Pula as duplicatas com status 'Finalizado'
            if duplicata['cessionaria_sacado_duplicata_status'] == "Finalizado":
                continue

            # Atualiza o status para 'Vencido' se a data de duplicata passou da data atual
            duplicata_data = datetime.fromtimestamp(duplicata['cessionaria_sacado_duplicadas_data'])
            if duplicata_data < data_atual:
                duplicata['cessionaria_sacado_duplicata_status'] = "Vencido"
            else:
                duplicata['cessionaria_sacado_duplicata_status'] = "A vencer"

        # Filtra as duplicatas pelo status atualizado
        duplicatas_filtradas = [
            duplicata for duplicata in duplicatas
            if duplicata['cessionaria_sacado_duplicata_status'] == status
        ]
    else:
        duplicatas_filtradas = []  # Se cessionaria_sacado não é um dicionário, não há duplicatas

    # Retorna todos os dados da cessionária, incluindo o cessionaria_sacado e as duplicatas filtradas
    return jsonify({
        "cessionaria_usuario_id": cessionaria.get("cessionaria_usuario_id"),
        "cessionaria_nome": cessionaria.get("cessionaria_nome"),
        "cessionaria_cnpj": cessionaria.get("cessionaria_cnpj"),
        "cessionaria_sacado": {
            "cessionaria_sacado_id": cessionaria["cessionaria_sacado"].get("cessionaria_sacado_id") if isinstance(
                cessionaria.get('cessionaria_sacado', {}), dict) else None,
            "cessionaria_sacado_nome": cessionaria["cessionaria_sacado"].get("cessionaria_sacado_nome") if isinstance(
                cessionaria.get('cessionaria_sacado', {}), dict) else None,
            "cessionaria_sacado_score": cessionaria["cessionaria_sacado"].get("cessionaria_sacado_score") if isinstance(
                cessionaria.get('cessionaria_sacado', {}), dict) else None,
            "duplicatas_filtradas": duplicatas_filtradas  # Duplicatas filtradas pelo status
        }
    }), 200
