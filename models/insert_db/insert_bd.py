import pymongo
import json
import bson  # Biblioteca para lidar com BSON

# Conexão com o cliente MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Acesso ao banco de dados e à coleção
db = client.get_database("BancoDeTeste")
collection = db.get_collection("assignee")


# Função para verificar se um documento cabe dentro do limite de 16MB
def documento_pequeno(documento):
    return len(bson.BSON.encode(documento)) < 16 * 1024 * 1024


# Abrir e ler o arquivo JSON
with open('cessionarias.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)  # Carregar o JSON como uma lista de dicionários Python

# Verificar se json_data é uma lista de documentos
if isinstance(json_data, list):
    documentos_validos = []
    total_inseridos = 0
    total_falhados = 0

    for documento in json_data:
        # Verificar se o documento é pequeno o suficiente para ser inserido
        if documento_pequeno(documento):
            documentos_validos.append(documento)
        else:
            print("Erro: Documento excede o limite de 16MB e não será inserido:",
                  documento.get('cessionaria_nome', 'Desconhecido'))
            total_falhados += 1

        # Inserir em lotes de 1000 documentos para evitar sobrecarga
        if len(documentos_validos) >= 1000:
            collection.insert_many(documentos_validos)
            total_inseridos += len(documentos_validos)
            documentos_validos = []  # Limpar a lista após a inserção

    # Inserir qualquer documento restante após o loop
    if documentos_validos:
        collection.insert_many(documentos_validos)
        total_inseridos += len(documentos_validos)

    print(f"Total de documentos inseridos: {total_inseridos}")
    print(f"Total de documentos não inseridos: {total_falhados}")

else:
    print("O arquivo JSON não contém uma lista de documentos.")

print("Inserção concluída com sucesso.")


