from models.app import mongo
from datetime import datetime

def insertSql():

    terms_collection = mongo.db.termo # colecao de termos do mongo db
    versionTerm = 1.0
    termo = [
        {
            "nome_termo": "Coleta e Uso de Dados",
            "descricao": "Coleta e Uso de Dados Ao aceitar estes termos, você autoriza a coleta, uso e compartilhamento de seus dados pessoais com terceiros para fins relacionados à prestação de nossos serviços. Isso pode incluir, mas não se limita a, empresas de análise de dados, plataformas de publicidade e parceiros comerciais.",
            "prioridade": 1,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        },
        {
            "nome_termo": "Compartilhamento",
            "descricao": "Finalidade do Compartilhamento Os dados coletados serão compartilhados com terceiros apenas quando necessário para: Melhorar a qualidade dos serviços prestados; Personalizar as ofertas e experiências para o usuário; Atender às exigências legais e regulatórias aplicáveis; Facilitar a execução de contratos e acordos. Proteção de Dados Nos comprometemos a garantir que todos os terceiros com quem compartilhamos seus dados tenham políticas de privacidade adequadas e utilizem os dados compartilhados em conformidade com a legislação vigente.",
            "prioridade": 1,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        },

        {
            "nome_termo": "Consentimento",
            "descricao": "Revogação de Consentimento Você tem o direito de revogar seu consentimento para o compartilhamento de dados a qualquer momento, solicitando a exclusão dos seus dados pessoais. No entanto, a revogação poderá impactar a prestação de determinados serviços.",
            "prioridade": 1,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        },
        {
            "nome_termo": "Direitos",
            "descricao": "Direitos do Usuário Você pode solicitar, a qualquer momento, o acesso aos seus dados, a correção de informações erradas ou incompletas, e a eliminação dos dados que não forem mais necessários para a prestação dos serviços.",
            "prioridade": 1,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        },
        {
            "nome_termo": "Recebimento de Email",
            "descricao": "Aceitação de Recebimento de Emails Ao aceitar estes termos, você concorda em receber comunicações por email, incluindo newsletters, atualizações, informações promocionais e convites para eventos. O envio dessas comunicações ocorrerá periodicamente, de acordo com as preferências que você selecionar.",
            "prioridade": 2,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        },
        {
            "nome_termo": "Conteúdo",
            "descricao": "Conteúdo dos Emails As comunicações enviadas podem incluir: Notícias e atualizações sobre nossos produtos e serviços; Ofertas especiais e promoções exclusivas; Informações relevantes sobre o setor ou tópicos de interesse. Cancelamento de Inscrição Você pode optar por não receber mais emails promocionais a qualquer momento,  licando no link 'Cancelar Inscrição' incluído na parte inferior de todos os emails que enviarmos. Essa ação não afetará a comunicação de emails relacionados ao seu uso dos nossos serviços, como notificações importantes.",
            "prioridade": 2,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        },
        {
            "nome_termo": "Protecao de Dados",
            "descricao": "Proteção de Dados Seu endereço de email será tratado de forma confidencial e não será compartilhado com terceiros sem o seu consentimento expresso, exceto conforme exigido por lei ou para a operação dos serviços solicitados.",
            "prioridade": 2,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        },
        {
            "nome_termo": "Frequencia",
            "descricao": "Frequência de Envio Tentamos limitar o número de emails enviados para garantir que nossas comunicações sejam relevantes e úteis. No entanto, o número de emails pode variar dependendo de promoções ou atualizações importantes.",
            "prioridade": 2,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "versao": versionTerm
        }
    ]

    for x in termo:
        existing_termo = terms_collection.find_one({'nome_termo': x['nome_termo']})

        if (existing_termo):
            continue
        else:
            terms_collection.insert_one(x)

    