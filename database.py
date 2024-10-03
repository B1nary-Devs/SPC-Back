import pymongo
from bson.json_util import dumps
from datetime import datetime

# Conexão com o cliente
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Acesso ou criação do banco de dados
db = client.get_database("BancoDeTeste")

# Acesso ou criação das collections
collectionsTermo = db.get_collection("termo")
collectionsUsuario = db.get_collection("usuario")




# # Função para inserir um novo usuário recebendo um JSON
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
                "termo_aceite": json_data["termo_aceite"],
                "termo_versao": json_data["termo_versao"],
                "termo": [
                    {
                        "descricao": json_data["descricao"],
                        "nome_termo": json_data["nome_termo"],
                        "data_cadastro": json_data["data_cadastro"],
                        "versao": json_data["versao"],
                        "termo_item": [
                            {
                                "item_nome": json_data["item_nome"],
                                "item_aceite": json_data["item_aceite"],
                                "item_data_update": json_data["data_update"],
                                "item_data_aceite": json_data["data_aceite"],
                                "item_prioridade": json_data["item_prioridade"],
                                "item_versao": json_data["item_versao"]
                            }
                        ],
                        "termo_log": [
                            {
                                "log_termo_nome": json_data["log_termo_nome"],
                                "log_termo_item": json_data["log_termo_item"],
                                "log_termo_status": json_data["log_termo_status"],
                                "log_termo_update": json_data["log_termo_update"],
                            }
                        ],
                    }
                ]

            }
        ]
    )



def main():
# Função principal para testes
    def createUsuarioComTermos(json_data):
        collectionsUsuario.insert_one(
            {
                "nome": json_data["nome"],
                "email": json_data["email"],
                "cpf_cnpj": json_data["cpf_cnpj"],
                "telefone": json_data["telefone"],
                "celular": json_data["celular"],
                "endereco": json_data["endereco"],
                "termo_aceite": json_data["termo_aceite"],
                "termo_versao": json_data["termo_versao"],
                "termo": [
                    {
                        "descricao": json_data["descricao_termo1"],
                        "nome_termo": json_data["nome_termo1"],
                        "data_cadastro": json_data["data_cadastro_termo1"],
                        "versao": json_data["versao_termo1"],
                        "termo_item": json_data["termo_item_termo1"],
                        "termo_log": json_data["termo_log_termo1"],
                    },
                    {
                        "descricao": json_data["descricao_termo2"],
                        "nome_termo": json_data["nome_termo2"],
                        "prioridade": json_data["prioridade_termo2"],
                        "data_cadastro": json_data["data_cadastro_termo2"],
                        "versao": json_data["versao_termo2"],
                        "termo_item": json_data["termo_item_termo2"],
                        "termo_log": json_data["termo_log_termo2"],
                    },
                ]
            }
        )


    # Exemplo de uso
    novo_usuario = {
        "nome": "Maria Oliveira",
        "email": "maria@example.com",
        "cpf_cnpj": "98765432100",
        "telefone": "1133445566",
        "celular": "11999887766",
        "endereco": "Avenida B, 456",
        "termo_aceite": "Sim",
        "termo_versao": "1.1",
        "descricao_termo1": "Primeiro termo de aceitação",
        "nome_termo1": "Termo A",
        "data_cadastro_termo1": datetime.now(),
        "versao_termo1": "1.0",
        "termo_item_termo1": [
            {
                "item_nome": "Item A1",
                "item_aceite": "Aceito",
                "item_data_update": datetime.now(),
                "item_data_aceite": datetime.now(),
                "item_prioridade": 1,
                "item_versao": "1.0"
            },
            {
                "item_nome": "Item A2",
                "item_aceite": "Aceito",
                "item_data_update": datetime.now(),
                "item_data_aceite": datetime.now(),
                "item_prioridade": 2,
                "item_versao": "1.0"
            }
        ],
        "termo_log_termo1": [
            {
                "log_termo_nome": "Log A1",
                "log_termo_item": "Item A1",
                "log_termo_status": "Aceito",
                "log_termo_update": datetime.now(),
            }
        ],
        "descricao_termo2": "Segundo termo de aceitação",
        "nome_termo2": "Termo B",
        "prioridade_termo2": 2,
        "data_cadastro_termo2": datetime.now(),
        "versao_termo2": "1.0",
        "termo_item_termo2": [
            {
                "item_nome": "Item B1",
                "item_aceite": "Aceito",
                "item_data_update": datetime.now(),
                "item_data_aceite": datetime.now(),
                "item_prioridade": 1,
                "item_versao": "1.0"
            },
            {
                "item_nome": "Item B2",
                "item_aceite": "Aceito",
                "item_data_update": datetime.now(),
                "item_data_aceite": datetime.now(),
                "item_prioridade": 2,
                "item_versao": "1.0"
            }
        ],
        "termo_log_termo2": [
            {
                "log_termo_nome": "Log B1",
                "log_termo_item": "Item B1",
                "log_termo_status": "Aceito",
                "log_termo_update": datetime.now(),
            }
        ],
    }

    createUsuarioComTermos(novo_usuario)
if __name__ == '__main__':
    main()