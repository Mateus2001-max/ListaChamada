import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import date
from Crud.GerenciadorAlunos import GerenciadorAlunos

def lista_presenca(alunos):
    st.title("📋 Lista de Presença")

    hoje = date.today().isoformat()
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute("SELECT aluno_id, presente FROM presencas WHERE data = ?", (hoje,))
    presencas = dict(cursor.fetchall())
    conn.close()

    # 🔹 Montar DataFrame com checkbox editável
    dados = []
    for i, aluno in enumerate(alunos, start=1):
        dados.append({
            "ID": i,
            "PRESENTE": bool(presencas.get(aluno.id, 0)),
            "NOME": aluno.nome,
            "RG": aluno.rg,
            "TURMA": aluno.turma
        })

    df = pd.DataFrame(dados)

    # 🔹 Editor interativo
    st.write("Edite os dados ou marque presença diretamente na tabela:")
    tabela_editada = st.data_editor(
        df,
        width="stretch",
        height=600,
        num_rows="dynamic",  # permite adicionar novas linhas
        key="tabela_presenca"
    )

    # 🔹 Botão para salvar alterações
    if st.button("💾 Salvar Alterações"):
        conn = sqlite3.connect("escola.db")
        cursor = conn.cursor()
        for _, linha in tabela_editada.iterrows():
            # Atualiza ou insere aluno usando ID como chave
            cursor.execute("""
                INSERT INTO alunos (id, nome, rg, turma)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET nome=excluded.nome, rg=excluded.rg, turma=excluded.turma
            """, (linha["ID"], linha["NOME"], linha["RG"], linha["TURMA"]))

            # Atualiza presença
            presente = 1 if linha["PRESENTE"] else 0
            cursor.execute("""
                INSERT INTO presencas (aluno_id, data, presente)
                VALUES (?, ?, ?)
                ON CONFLICT(aluno_id, data) DO UPDATE SET presente=excluded.presente
            """, (linha["ID"], hoje, presente))
        conn.commit()
        conn.close()
        st.success("✅ Alterações salvas com sucesso!")

    # Botão para excluir alunos removidos da tabela
    if st.button("🗑️ Remover alunos excluídos"):
        conn = sqlite3.connect("escola.db")
        cursor = conn.cursor()

        # Pegar IDs atuais da tabela editada
        ids_atuais = set(tabela_editada["ID"].dropna().astype(int))

        # Buscar todos os IDs existentes no banco
        cursor.execute("SELECT id FROM alunos")
        ids_banco = set(row[0] for row in cursor.fetchall())

        # Descobrir quais foram removidos
        ids_removidos = ids_banco - ids_atuais

        # Excluir do banco
        for id_removido in ids_removidos:
            cursor.execute("DELETE FROM alunos WHERE id=?", (id_removido,))

        conn.commit()
        conn.close()
        st.success("✅ Alunos removidos do banco com sucesso!")
        st.rerun()
    # 🔹 Estatísticas
    total = len(tabela_editada)
    presentes = sum(bool(x) for x in tabela_editada["PRESENTE"])
    porcentagem = (presentes / total) * 100 if total > 0 else 0

    st.write(f"**Total de alunos:** {total}")
    st.write(f"**Presentes:** {presentes}")
    st.progress(porcentagem / 100)
    st.success(f"**Porcentagem de presença:** {porcentagem:.2f}%")
    
    # Criar uma cópia formatada do DataFrame
    df_download = tabela_editada.copy()
    df_download["PRESENTE"] = df_download["PRESENTE"].apply(lambda x: "Sim" if x else "Não")
    df_download = df_download[["ID", "PRESENTE", "NOME", "RG", "TURMA"]]


    # Calcular estatísticas
    total = len(df_download)
    presentes = sum(df_download["PRESENTE"] == "Sim")
    porcentagem = (presentes / total * 100) if total > 0 else 0

    # Adicionar linha de resumo ao final
    resumo = pd.DataFrame([{
        "ID": "Resumo",
        "NOME": "",
        "RG": "",
        "TURMA": "",
        "PRESENTE": f"{presentes}/{total} ({porcentagem:.2f}%)"
    }])
    df_final = pd.concat([df_download, resumo], ignore_index=True)

    # Converter DataFrame para Excel em memória
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Presenca")

    # Botão para baixar
    st.download_button(
        label="📥 Baixar presença de hoje",
        data=buffer.getvalue(),
        file_name=f"presenca_{date.today().isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 🔹 Chamada da função
ger = GerenciadorAlunos()
alunos = ger.listar()

if alunos:
    lista_presenca(alunos)
else:
    st.warning("Nenhum aluno cadastrado no banco de dados.")

