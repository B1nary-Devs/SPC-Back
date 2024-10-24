import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

credenciais = {
  "type": os.getenv('TYPE'),
  "project_id": os.getenv('PROJECT_ID'),
  "private_key_id": os.getenv('PRIVATE_KEY_ID'),
  "private_key": os.getenv('PRIVATE_KEY'),
  "client_email": os.getenv('CLIENT_EMAIL'),
  "client_id": os.getenv('CLIENT_ID'),
  "auth_uri": os.getenv('AUTH_URI'),
  "token_uri": os.getenv('TOKEN_URI'),
  "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
  "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL'),
  "universe_domain": os.getenv('UNIVERSE_DOMAIN')
}


# Função para ler emails da planilha
def ler_emails_da_planilha():
    # Definir o escopo
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Autenticar com a conta de serviço
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credenciais, scope)
    client = gspread.authorize(credentials)

    # Abrir a planilha
    sheet = client.open("Notificacao").sheet1  # Substitua pelo nome da sua planilha

    # Ler todas as linhas da planilha (pulando o cabeçalho)
    dados = sheet.get_all_records()

    # Coletar os emails da coluna 'email'
    emails = [dado['email'] for dado in dados]
    return emails


# Função para enviar o email
def enviar_email(para_email, assunto, mensagem, seu_email, senha_email):
    try:
        # Configuração do servidor SMTP
        servidor = smtplib.SMTP('smtp.gmail.com', 587)  # Para o Gmail
        servidor.starttls()  # Iniciar comunicação segura
        servidor.login(seu_email, senha_email)

        # Compor a mensagem
        msg = MIMEMultipart()
        msg['From'] = seu_email
        msg['To'] = para_email
        msg['Subject'] = assunto

        # Adicionar o corpo da mensagem
        msg.attach(MIMEText(mensagem, 'plain'))

        # Enviar o email
        servidor.sendmail(seu_email, para_email, msg.as_string())
        servidor.quit()
        print(f"Email enviado com sucesso para {para_email}")

    except Exception as e:
        print(f"Erro ao enviar email para {para_email}: {e}")


# Função principal que lê emails e envia a mensagem
def enviar_emails_para_planilha():
    seu_email = os.getenv('EMAIL')  # Substitua pelo seu email
    senha_email = os.getenv('PASSWORD')  # Substitua pela senha do seu email (use senhas de app para Gmail)
    assunto = "Vazou email"
    mensagem = "O seu email vazou."

    # Ler os emails da planilha
    emails = ler_emails_da_planilha()

    # Enviar email para cada um
    for email in emails:
        enviar_email(email, assunto, mensagem, seu_email, senha_email)


