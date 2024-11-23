import json
import requests

# URL da API
API_URL = "http://127.0.0.1:5000/assignee/createAssignee"

# Função para carregar o JSON e enviar requisições para a API
def carregar_e_inserir_cessionarias(arquivo_json):
    # Abrir e ler o arquivo JSON
    with open(arquivo_json, 'r', encoding='utf-8') as file:
        json_data = json.load(file)  # Carregar o JSON como uma lista de dicionários Python

    # Verificar se json_data é uma lista de documentos
    if not isinstance(json_data, list):
        print("Erro: O arquivo JSON não contém uma lista de documentos.")
        return

    total_inseridos = 0
    total_falhados = 0

    # Iterar sobre cada cessionária no JSON
    for cessionaria in json_data:
        try:
            # Enviar uma requisição POST para a API
            response = requests.post(API_URL, json=cessionaria)

            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 201:
                total_inseridos += 1
            else:
                total_falhados += 1

        except Exception as e:
            total_falhados += 1

    # Resumo da operação
    print(f"Total de cessionárias inseridas com sucesso: {total_inseridos}")
    print(f"Total de cessionárias que falharam: {total_falhados}")

# Executar a função com o caminho para o arquivo JSON
carregar_e_inserir_cessionarias('cessionaria3.txt')
