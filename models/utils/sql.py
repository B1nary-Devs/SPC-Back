from models.app import mongo
from datetime import datetime

def insertSql():
    insertTermo()
    insertAdmin()
   

def insertTermo():
    try:
        terms_collection = mongo.db.termo # colecao de termos do mongo db
        versionTerm = 1.0
        termo = [
            {          
                'nome_termo': 'termo de uso',
                'descricao': "Ao aceitar estes termos, você autoriza a coleta, uso e compartilhamento de seus dados pessoais com terceiros para fins relacionados à prestação de nossos serviços. Isso pode incluir, mas não se limita a, empresas de análise de dados, plataformas de publicidade e parceiros comerciais. \n\n**Finalidade do Compartilhamento:** Os dados coletados serão compartilhados com terceiros apenas quando necessário para: \n- Melhorar a qualidade dos serviços prestados; \n- Personalizar as ofertas e experiências para o usuário; \n- Atender às exigências legais e regulatórias aplicáveis; \n- Facilitar a execução de contratos e acordos. \n\n**Proteção de Dados:** Nos comprometemos a garantir que todos os terceiros com quem compartilhamos seus dados possuam políticas de privacidade adequadas e utilizem os dados compartilhados em conformidade com a legislação vigente. \n\n**Revogação de Consentimento:** Você tem o direito de revogar seu consentimento para o compartilhamento de dados a qualquer momento, solicitando a exclusão dos seus dados pessoais. No entanto, a revogação poderá impactar a prestação de determinados serviços. \n\n**Direitos do Usuário:** Você pode solicitar, a qualquer momento: \n- Acesso aos seus dados; \n- Correção de informações erradas ou incompletas; \n- Eliminação de dados que não forem mais necessários para a prestação dos serviços. \n\n**Alterações no Termo de Uso:** Nos reservamos o direito de atualizar este Termo de Uso a qualquer momento. As alterações entrarão em vigor a partir da data de publicação.",     
                'prioridade': 1,                             
                'data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),               
                'versao': versionTerm,                               
                'termo_item': [
                    {
                        'termo_item_nome': 'recebimento de email',  
                        'termo_item_descricao': 'Ao aceitar este termo, você concorda em receber comunicações por email, incluindo newsletters, atualizações, informações promocionais e convites para eventos. As comunicações serão enviadas periodicamente, conforme suas preferências.',       
                        'termo_item_data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),        
                        'termo_item_prioridade': 2,                    
                        'termo_item_versao': versionTerm 
                    },
                    {
                        'termo_item_nome': 'conteudo', 
                        'termo_item_descricao': 'As comunicações podem incluir: notícias e atualizações sobre produtos e serviços; ofertas especiais e promoções; e informações relevantes sobre o setor ou tópicos de interesse. Você pode optar por não receber mais emails promocionais a qualquer momento, clicando no link "Cancelar Inscrição" nos emails. Essa ação não afetará comunicações importantes relacionadas ao uso de nossos serviços.',       
                        'termo_item_data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),        
                        'termo_item_prioridade': 2,                    
                        'termo_item_versao': versionTerm 
                    },
                    {
                        'termo_item_nome': 'protecao de dados',  
                        'termo_item_descricao': 'Seu endereço de email será tratado com confidencialidade e não será compartilhado com terceiros sem o seu consentimento, exceto quando exigido por lei ou para a operação dos serviços solicitados.',       
                        'termo_item_data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),        
                        'termo_item_prioridade': 2,                    
                        'termo_item_versao': versionTerm 
                    },
                    {
                    
                        'termo_item_nome': 'frequencia',  
                        'termo_item_descricao': 'Nós limitamos o número de emails enviados para garantir que as comunicações sejam relevantes. No entanto, a frequência pode variar conforme promoções ou atualizações importantes.',       
                        'termo_item_data_cadastro': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),        
                        'termo_item_prioridade': 2,                    
                        'termo_item_versao': versionTerm 
                    }
                ]
            }
        ]

        for x in termo:
            existing_termo = terms_collection.find_one({'nome_termo': x['nome_termo']})

            if (existing_termo):
                continue
            else:
                terms_collection.insert_one(x)    

    except Exception as e:
        print(f"Erro: {str(e)}")

def insertAdmin():
    try:
        users_collection = mongo.db.usuario # colecao de usuario do mongo db
        versionTerm = 1.0
        user = {        
            "nome": "Administrador",            
            "email": "administrador@admin.com",
            "senha": "admin",
            "perfil": 'Admin', 
            "cpf_cnpj": "0",   
            "telefone": "00000000",    
            "celular": "00000000",
            "cep": 00000000,
            "endereco": "Rua Exemplo, 123",     
            "termo_atual": {                
                "termo_nome": "termo de uso",  
                "termo_aceite": True,
                "termo_versao": versionTerm,
                "termo_item": [
                    {
                        "termo_item_nome": "recebimento de email",
                        "termo_item_aceite": True
                    },
                    {
                        "termo_item_nome": "conteudo",
                        "termo_item_aceite": False
                    },
                    {
                        "termo_item_nome": "protecao de dados",
                        "termo_item_aceite": True
                    },
                    {
                        "termo_item_nome": "frequencia",
                        "termo_item_aceite": True
                    }
                ]                
            },
            "termo_log": []
        }
        nome = user['nome']
        existing_user = users_collection.find_one({'nome': nome})
        if not existing_user:
            users_collection.insert_one(user)
        

    except Exception as e:
        print(f"Erro: {str(e)}")        