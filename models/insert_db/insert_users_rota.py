import json
import requests

# URL da API para criação de usuários
API_URL = "http://127.0.0.1:5000/users/createUser"

# Função para carregar o JSON e enviar requisições para a API
def carregar_e_inserir_usuarios(arquivo_json):
    # Abrir e ler o arquivo JSON
    with open(arquivo_json, 'r', encoding='utf-8') as file:
        json_data = json.load(file)  # Carregar o JSON como uma lista de dicionários Python

    # Verificar se json_data é uma lista de documentos
    if not isinstance(json_data, list):
        print("Erro: O arquivo JSON não contém uma lista de documentos.")
        return

    total_inseridos = 0
    total_falhados = 0

    # Iterar sobre cada usuário no JSON
    for usuario in json_data:
        try:
            # Enviar uma requisição POST para a API
            response = requests.post(API_URL, json=usuario)

            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 201:
                total_inseridos += 1
            else:
                print(f"Erro ao inserir usuário {usuario.get('username', 'Desconhecido')}: {response.json().get('error')}")
                total_falhados += 1

        except Exception as e:
            print(f"Exceção ao inserir usuário {usuario.get('username', 'Desconhecido')}: {str(e)}")
            total_falhados += 1

    # Resumo da operação
    print(f"Total de usuários inseridos com sucesso: {total_inseridos}")
    print(f"Total de usuários que falharam: {total_falhados}")

# Executar a função com o caminho para o arquivo JSON
carregar_e_inserir_usuarios('usuarios.json')
