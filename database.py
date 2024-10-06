import pymongo
from bson.json_util import dumps
from datetime import datetime
from bson.objectid import ObjectId

# Conexão com o cliente
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Acesso ou criação do banco de dados
db = client.get_database("BancoDeTeste")

# Acesso ou criação das collections
collectionsTermo = db.get_collection("termo")
collectionsUsuario = db.get_collection("usuario")

# Função para inserir um novo usuário recebendo um JSON
def createUsuario(json_data):
    collectionsUsuario.insert_many(
        [
            {
                "nome": json_data["nome"],
                "email": json_data["email"],
                "cpf_cnpj": json_data["cpf_cnpj"],
                "telefone": json_data["telefone"],
                "celular": json_data["celular"],
                "endereco": json_data["endereco"],
                "termo_atual_aceite": json_data["termo_atual_aceite"],
                "termo_versao": json_data["termo_versao"],
                "termo_status": {
                    "termo_nome": json_data["termo_nome"],
                    "termo_aceite": json_data["termo_aceite"],
                },
                "termo_log": [
                    {
                        "termo_log_nome": log["termo_log_nome"],
                        "termo_log_item_status": log["termo_log_item_status"],
                        "termo_log_item_update_data": log["termo_log_item_update_data"],
                    } for log in json_data["termo_log"]
                ]
            }
        ]
    )

def createTermo(json_data):
    collectionsTermo.insert_many(
        [
            {
                "descricao": json_data["descricao"],
                "nome_termo": json_data["nome_termo"],
                "prioridade": json_data["prioridade"],
                "data_cadastro": json_data["data_cadastro"],
                "versao": json_data["versao"],
                "termo_item": {
                    "termo_item_item_nome": json_data["termo_item_nome"],
                    "termo_item_item_aceite": json_data["termo_item_aceite"],
                    "termo_item_data_update": json_data["termo_item_data_update"],
                    "termo_item_data_aceite": json_data["termo_item_data_aceite"],
                    "termo_item_prioridade": json_data["termo_item_prioridade"],
                    "termo_item_item_versao": json_data["termo_item_versao"],
                },
            }
        ]
    )


def main():
    # Função principal para testes
    json_data_usuario = {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "cpf_cnpj": "123.456.789-00",
        "telefone": "(11) 1234-5678",
        "celular": "(11) 91234-5678",
        "endereco": "Rua Exemplo, 123, São Paulo, SP",
        "termo_atual_aceite": True,
        "termo_versao": 1.2,
        "termo_nome": "Termo de Uso Padrão",
        "termo_aceite": True,
        "termo_log": [
            {
                "termo_log_nome": "Termo Log Inicial",
                "termo_log_item_status": [True, False, True, False, True],
                "termo_log_item_update_data": "2024-10-04"
            }
        ]
    }

    json_data_termo = {
        "descricao": "Termo para uso da plataforma",
        "nome_termo": "Termo de Uso Padrão",
        "prioridade": 1,
        "data_cadastro": "2023-10-01",
        "versao": 1,
        "termo_item_nome": "Termo para Cadastro",
        "termo_item_aceite": True,
        "termo_item_data_update": "2023-10-04",
        "termo_item_data_aceite": "2023-10-04",
        "termo_item_prioridade": 1,
        "termo_item_versao": 1.0
    }

    item_data = {
        "termo_item_nome": "Novo Item do Termo",
        "termo_item_aceite": False,
        "termo_item_data_update": "2023-10-05",
        "termo_item_data_aceite": "2023-10-05",
        "termo_item_prioridade": 2,
        "termo_item_versao": 1.0
    }

    def adicionarNovoLogUsuario(usuario_id_str):
        usuario_id = ObjectId(usuario_id_str)
        novo_log = {
            "termo_log_nome": "Novo Termo Log",
            "termo_log_item_status": [False, False, False, False, False],  # Lista com 5 booleans fixos
            "termo_log_item_update_data": "2023-10-04"
        }

        # Verifique se o usuário existe antes de adicionar o log
        usuario = collectionsUsuario.find_one({"_id": usuario_id})
        if usuario:
            collectionsUsuario.update_one(
                {"_id": usuario_id},
                {"$push": {"termo_log": novo_log}}  # Adicionando um novo log à lista de logs
            )
            print(f"Novo log adicionado para o usuário: {usuario['nome']}")
        else:
            print("Usuário não encontrado.")

    def adicionarItemTermo(termo_id, item_data):
        collectionsTermo.update_one(
            {"_id": termo_id},
            {"$set": {
                "termo_item.termo_item_item_nome": item_data["termo_item_nome"],
                "termo_item.termo_item_aceite": item_data["termo_item_aceite"],
                "termo_item.termo_item_data_update": item_data["termo_item_data_update"],
                "termo_item.termo_item_data_aceite": item_data["termo_item_data_aceite"],
                "termo_item.termo_item_prioridade": item_data["termo_item_prioridade"],
                "termo_item.termo_item_versao": item_data["termo_item_versao"]
            }}
        )

    def adicionarTermoUsuario(usuario_id, termo_data):
        collectionsUsuario.update_one(
            {"_id": usuario_id},
            {"$set": {
                "termo_status": {
                    "termo_nome": termo_data["termo_nome"],
                    "termo_aceite": termo_data["termo_aceite"]
                },
                "termo_versao": termo_data["termo_versao"]
            }}
        )

    def createUsuarioComTermo(json_data_usuario, json_data_termo):
        createUsuario(json_data_usuario)
        createTermo(json_data_termo)

    # Obtém o ID do usuário e do termo (assumindo que são os últimos inseridos)
    usuario_id = collectionsUsuario.find_one({"nome": "João Silva"})["_id"]
    termo_id = collectionsTermo.find_one({"nome_termo": "Termo de Uso Padrão"})["_id"]

    # Dados para adicionar termo ao usuário
    termo_usuario_data = {
        "termo_nome": "Termo de Uso Padrão",
        "termo_aceite": True,
        "termo_versao": 1.0
    }

    # Adiciona o termo ao usuário
    adicionarTermoUsuario(usuario_id, termo_usuario_data)

    # Dados para adicionar um item ao termo
    item_data = {
        "termo_item_nome": "Novo Item do Termo",
        "termo_item_aceite": False,
        "termo_item_data_update": "2023-10-05",
        "termo_item_data_aceite": "2023-10-05",
        "termo_item_prioridade": 2,
        "termo_item_versao": 1.0
    }

    # Adiciona o item ao termo
    # adicionarItemTermo(termo_id, item_data)
    createUsuarioComTermo(json_data_usuario,json_data_termo)
    # adicionarNovoLogUsuario("6700657a0696bb0ed22be0ad")
if __name__ == '__main__':
    main()