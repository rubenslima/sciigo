import os
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Definir e-mail e senha do remetente a partir das variáveis de ambiente
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

# Função para enviar e-mail
def send_email(receiver_email, subject, content):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Adicionando o corpo do texto
        msg.attach(MIMEText(content, 'plain'))

        # Configurando o servidor Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, receiver_email, text)
        server.quit()

        return True
    except Exception as e:
        st.error(f"Erro ao enviar o e-mail: {str(e)}")
        return False

# Função para salvar no banco de dados
def save_to_db(receiver_email, subject, date_sent):
    conn = sqlite3.connect('emails_sent.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS emails 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      email TEXT, subject TEXT, date_sent TEXT)''')
    cursor.execute('INSERT INTO emails (email, subject, date_sent) VALUES (?, ?, ?)',
                   (receiver_email, subject, date_sent))
    conn.commit()
    conn.close()

# Interface com Streamlit
st.title("Envio de E-mails com Streamlit")

# Caminho fixo da pasta 'models'
models_dir = os.path.join(os.getcwd(), "models")

# Listar arquivos .txt na pasta 'models'
txt_files = [f for f in os.listdir(models_dir) if f.endswith('.txt')]

# Verifica se há arquivos .txt na pasta 'models'
if txt_files:
    selected_file = st.selectbox("Selecione o arquivo de texto para usar:", txt_files)
    
    # Carregar o conteúdo do arquivo selecionado
    txt_file_path = os.path.join(models_dir, selected_file)
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        st.text_area("Conteúdo do e-mail", content, height=300)
else:
    st.error("Nenhum arquivo .txt encontrado na pasta 'models'.")

# Entrada do e-mail de destino
receiver_email = st.text_input("Digite o e-mail de destino:")

# Assunto do e-mail
subject = st.text_input("Assunto do e-mail:")

# Botão para enviar o e-mail
if st.button("Enviar E-mail"):
    if receiver_email and subject and content:
        if send_email(receiver_email, subject, content):
            st.success(f"E-mail enviado para {receiver_email}")
            save_to_db(receiver_email, subject, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.info(f"E-mail registrado no banco de dados.")
    else:
        st.warning("Preencha todos os campos antes de enviar.")

# Visualizando e-mails enviados
if st.button("Ver E-mails Enviados"):
    conn = sqlite3.connect('emails_sent.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            st.write(f"ID: {row[0]} | E-mail: {row[1]} | Assunto: {row[2]} | Data: {row[3]}")
    else:
        st.write("Nenhum e-mail enviado registrado.")
