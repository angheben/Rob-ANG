import gspread
from twilio.rest import Client
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import os

# Configurações Twilio (ATUALIZE COM SUAS CREDENCIAIS REAIS)
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")

# Configurações Google Sheets (ATUALIZE COM SEUS DADOS)
SHEET_URL = os.getenv("GOOGLE_SHEETS_URL")
SHEET_NAME = "Status"

# Configurar acesso à planilha
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(creds)

# Inicializar cliente Twilio
twilio_client = Client(account_sid, auth_token)


def formatar_data(data_str):
    """Formata a data para exibição mais amigável"""
    if not data_str:
        return "a definir"
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return data_str


def enviar_mensagem_whatsapp(destinatario, mensagem):
    """Envia mensagem via WhatsApp usando Twilio"""
    try:
        message = twilio_client.messages.create(
            body=mensagem,
            from_=twilio_number,
            to=f"whatsapp:{destinatario}"
        )
        print(f"Mensagem enviada para {destinatario}: {message.sid}")
        return True
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False


def ler_planilha():
    """Lê os dados da planilha e retorna como lista de dicionários"""
    try:
        sheet = client.open_by_url(SHEET_URL).worksheet(SHEET_NAME)
        dados = sheet.get_all_records()
        return dados
    except Exception as e:
        print(f"Erro ao ler planilha: {e}")
        return None


def gerar_mensagem(cliente):
    """Gera a mensagem personalizada com base nos dados do cliente"""
    mensagem = f"""
*Atualização do Processo - {cliente['Processo']}*

👋 Olá *{cliente['Cliente']}*, aqui é o robô da ANG, estarei atualizando vc sobre o seu processo:

📦 *Produto:* {cliente['Produto']}
🔄 *Status:* {cliente['Status']}
✅ *Prontidão da Mercadoria:* {formatar_data(cliente['Prontidão da Mercadoria'])}
🚢 *Previsão de Embarque:* {formatar_data(cliente['Previsão de Embarque'])}
🏭 *Previsão de Chegada:* {formatar_data(cliente['Previsão de Chegada'])}
📄 *Documentos:* {cliente['Documentos']}
🚛 *Agente de Frete:* {cliente['Agente de Frete']}
🕒 *Última Atualização:* {formatar_data(cliente['Última Atualização'])}

Qualquer dúvida, estamos à disposição!
    """
    return mensagem.strip()


def main():
    print("Iniciando robô de atualização de processos...")
    dados = ler_planilha()

    if dados:
        for cliente in dados:
            telefone = cliente.get('Telefone', '')
            if telefone and cliente.get('Status') not in ['Finalizado', 'Cancelado']:
                mensagem = gerar_mensagem(cliente)
                print(f"Preparando mensagem para {cliente['Cliente']}...")
                enviar_mensagem_whatsapp(telefone, mensagem)


def teste_conexao():
    try:
        sheet = client.open_by_url(SHEET_URL).worksheet(SHEET_NAME)
        print("✅ Conexão com Google Sheets OK!")
        print(f"→ Primeira célula: {sheet.acell('A1').value}")
        return True
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def teste_twilio():
    try:
        test_msg = twilio_client.messages.create(
            body="Teste de conexão Twilio",
            from_=twilio_number,
            to="whatsapp:+554195038583"  # Substitua pelo SEU número
        )
        print(f"✅ Twilio OK! SID: {test_msg.sid}")
        return True
    except Exception as e:
        print(f"❌ Twilio Error: {str(e)}")
        return False


if __name__ == "__main__":
    main()
