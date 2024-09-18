import pymongo
from bson.json_util import dumps

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
                "termo_status": [
                    {
                        "nome_termo": json_data["nome_termo"],
                        "versao": json_data["versao"],
                        "prioridade": json_data["prioridade"],
                        "data_aceite": json_data["data_aceite"],
                        "data_update": json_data["data_update"],
                        "aceite": json_data["aceite"]
                    }
                ]
            }
        ]
    )


# Função para inserir um novo termo recebendo um JSON
def createTermo(json_data):
    collectionsTermo.insert_many(
        [
            {
                "descricao": json_data["descricao"],
                "nome_termo": json_data["nome_termo"],
                "prioridade": json_data["prioridade"],
                "data_cadastro": json_data["data_cadastro"],
                "versao": json_data["versao"]
            }
        ]
    )


# Função para atualizar um usuário pelo CPF/CNPJ, recebendo um JSON
def updateUsuario(json_data):
    collectionsUsuario.update_one(
        {"cpf_cnpj": json_data["cpf_cnpj"], "termo_status.nome_termo": json_data["nome_termo"]},
        {
            "$set": {
                "nome": json_data["nome"],
                "email": json_data["email"],
                "telefone": json_data["telefone"],
                "celular": json_data["celular"],
                "endereco": json_data["endereco"]
            }
        }
    )


# Função para ler um usuário pelo CPF/CNPJ recebendo JSON
def readUsuarioCpfCnpj(json_data):
    result = collectionsUsuario.find({"cpf_cnpj": json_data["cpf_cnpj"]})
    json_result = dumps(result)  # Converte o cursor do MongoDB em JSON
    return json_result


# Função para retornar termos e condições com base em JSON
def readTermoCondicoes(json_data):
    result = collectionsTermo.find_one({"nome_termo": json_data["nome_termo"], "versao": json_data["versao"]})
    json_result = dumps(result)  # Converte o cursor do MongoDB em JSON
    return json_result


# Função para retornar todos os usuários e retornar os dados em formato JSON
def readTodosUsuarios():
    result = collectionsUsuario.find()  # Busca todos os documentos na coleção
    json_result = dumps(result)  # Converte o cursor do MongoDB em JSON
    return json_result


# Função para deletar um usuário pelo CPF/CNPJ
def deleteUsuario(cpf_cnpj):
    collectionsUsuario.delete_one({"cpf_cnpj": cpf_cnpj})
    return f"Usuário com CPF/CNPJ {cpf_cnpj} foi deletado."


# Função para retornar os termos obrigatórios com a versão mais atualizada
def readTermosObrigatoriosAtualizados():
    result = collectionsTermo.find({"prioridade": "obrigatorio"}).sort("versao", -1).limit(1)
    json_result = dumps(result)  # Converte o cursor do MongoDB em JSON
    return json_result


# Função para retornar os termos não obrigatórios com a versão mais atualizada
def readTermosNaoObrigatoriosAtualizados():
    result = collectionsTermo.find({"prioridade": "nao-obrigatorio"}).sort("versao", -1).limit(1)
    json_result = dumps(result)  # Converte o cursor do MongoDB em JSON
    return json_result


# Função para retornar todos os termos e versões aceitas ou não de um usuário
def readTermosUsuario(cpf_cnpj):
    result = collectionsUsuario.find_one({"cpf_cnpj": cpf_cnpj}, {"_id": 0, "termo_status": 1})
    json_result = dumps(result)  # Converte o cursor do MongoDB em JSON
    return json_result


# Função para verificar a versão do termo aceito pelo usuário e a última versão criada
def verificarVersaoTermoUsuario(json_data):
    usuario = collectionsUsuario.find_one({"cpf_cnpj": json_data["cpf_cnpj"], "termo_status.nome_termo": json_data["nome_termo"]})
    if usuario:
        termo_aceito = max(usuario["termo_status"], key=lambda t: t["versao"] if t["nome_termo"] == json_data["nome_termo"] else 0)
        ultima_versao_termo = collectionsTermo.find_one({"nome_termo": json_data["nome_termo"]}, sort=[("versao", -1)])

        return {
            "versao_aceita": termo_aceito["versao"],
            "ultima_versao": ultima_versao_termo["versao"]
        }
    return "Usuário ou termo não encontrado."


# Função principal para testes
def main():
    # Testando a criação e atualização de dados com JSON
    usuario_json = {
        "nome": "nome",
        "email": "email",
        "cpf_cnpj": "cpf6",
        "telefone": "telefone",
        "celular": "celular",
        "endereco": "endereco",
        "nome_termo": "nome_termo",
        "versao": "3",
        "prioridade": "obrigatorio",
        "data_aceite": "data_aceite",
        "data_update": "data_update",
        "aceite": "aceite"
    }

    createUsuario(usuario_json)

    termo_json = {
        "descricao": "descricao",
        "nome_termo": "nome",
        "prioridade": "obrigatorio",
        "data_cadastro": "data",
        "versao": "3"
    }

    createTermo(termo_json)

    # Testando as funções de leitura com JSON
    cpf_json = {"cpf_cnpj": "cpf6"}
    usuario_json = readUsuarioCpfCnpj(cpf_json)
    print(usuario_json)

    termo_condicoes_json = {
        "nome_termo": "nome",
        "versao": "3"
    }
    termo_condicoes = readTermoCondicoes(termo_condicoes_json)
    print(termo_condicoes)

    # Função para verificar versão do termo com JSON
    versao_json = {
        "cpf_cnpj": "cpf6",
        "nome_termo": "nome_termo"
    }
    versao_termo = verificarVersaoTermoUsuario(versao_json)
    print(versao_termo)


if __name__ == '__main__':
    main()