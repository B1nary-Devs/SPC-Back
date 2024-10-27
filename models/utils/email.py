import os

def registraEmail(nome, email):
    try:
        utils_dir = os.path.dirname(os.path.abspath(__file__))  
        file_path = os.path.join(utils_dir, 'user_register.txt')
        
        file = open(file_path, 'a')
        file.write(f"Nome: {nome}, Email: {email}\n")
        file.close()
        
        print('Email registrado com sucesso!')           
    except Exception as e:
        print(f"Erro: {str(e)}")