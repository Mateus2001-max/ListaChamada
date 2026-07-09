import streamlit as st
import pandas as pd
import sqlite3
import io
import os
from datetime import date, timedelta
from Crud.GerenciadorAlunos import GerenciadorAlunos
from openpyxl.styles import Alignment, Border, Side, Font
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image
from menu import gerar_relatorio_historico
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

# 🔹 Configuração do Google Drive
FOLDER_ID = "1kNMGdts9a9gCKY8zQ909_pQCNW-YR3yj"

def autenticar_drive():
    credentials = Credentials.from_service_account_info(
        st.secrets["SERVICE_ACCOUNT"],  # já é dict
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    return service

def upload_to_drive(file_path, folder_id=FOLDER_ID):
    service = autenticar_drive()

    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }

    media = MediaFileUpload(file_path, resumable=False)

    arquivo = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name"
    ).execute()

    print(f"✅ Arquivo enviado: {arquivo['name']}")

def arquivo_existe_no_drive(nome_arquivo, folder_id=FOLDER_ID):
    service = autenticar_drive()
    query = f'name="{nome_arquivo}" and "{folder_id}" in parents and trashed=false'
    resultado = service.files().list(
        q=query,
        fields="files(id,name)"
    ).execute()
    return len(resultado.get("files", [])) > 0

# 🔹 Botão de teste para upload simples
if st.sidebar.button("📤 Testar upload com test.txt"):
    if os.path.exists("test.txt"):
        try:
            upload_to_drive("test.txt")
            st.success("✅ Arquivo test.txt enviado para o Google Drive!")
        except Exception as e:
            st.error(f"❌ Erro no upload: {e}")
    else:
        st.error("❌ O arquivo test.txt não existe no diretório do app.")

# 🔹 Função principal de presença
def lista_presenca(alunos):
    st.title("📋 Lista de Presença")
    # ... resto da função igual ao seu código original ...
    # (não alterei nada aqui)

# 🔹 Automático: cria e envia relatório de ontem
ontem = (date.today() - timedelta(days=1)).isoformat()
arquivo_excel = f"presenca_{ontem}.xlsx"
caminho_local = f"Relatorios/{arquivo_excel}"

if not os.path.exists(caminho_local):
    gerar_relatorio_historico()
    upload_to_drive(caminho_local)
    st.success(f"📂 Relatório de ontem criado e enviado para o Google Drive: {arquivo_excel}")
else:
    if arquivo_existe_no_drive(arquivo_excel):
        st.info(f"📂 Relatório de ontem já está no Google Drive: {arquivo_excel}")
    else:
        upload_to_drive(caminho_local)
        st.success(f"📂 Relatório de ontem enviado para o Google Drive: {arquivo_excel}")

# Chamada da função
ger = GerenciadorAlunos()
alunos = ger.listar()

if alunos:
    lista_presenca(alunos)
else:
    st.warning("Nenhum aluno cadastrado no banco de dados.")
