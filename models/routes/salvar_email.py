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

def salvar_no_google_sheets(nome, email):
    # Definir o escopo para acessar o Google Sheets e o Google Drive
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Autenticar com a conta de serviço usando o arquivo credentials.json
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credenciais, scope)
    client = gspread.authorize(credentials)

    # Abrir a planilha pelo nome
    sheet = client.open("Notificacao").sheet1  # Substitua pelo nome da sua planilha

    # Adicionar uma nova linha com nome e email
    sheet.append_row([nome, email])
