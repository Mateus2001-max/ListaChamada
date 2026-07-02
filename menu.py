from Crud.GerenciadorAlunos import GerenciadorAlunos
from Interface.Interface_tkinter import  abrir_lista_presenca
from datetime import datetime
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
import pandas as pd
import sqlite3
from datetime import date, timedelta
def exibir_menu():
    gerar_relatorio_historico()
    
    ger = GerenciadorAlunos()

    while True:
        print("\n===== MENU ALUNOS =====")
        print("1 - Cadastrar aluno")
        print("2 - Listar alunos")
        print("3 - Atualizar aluno")
        print("4 - Remover aluno")
        print("5 - Lista de Presença")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Digite o nome do aluno: ")
            rg = input("Digite o RG do aluno: ")
            turma = input("Digite a turma do aluno (ex: 3º ano E.M): ")
            ger.adicionar(nome, rg, turma)
            print("Aluno cadastrado com sucesso!")


        elif opcao == "2":
            alunos = ger.listar()
            if alunos:
                for aluno in alunos:
                    print(aluno)
            else:
                print("Nenhum aluno cadastrado.")

        elif opcao == "3":
            id = int(input("Digite o ID do aluno a atualizar: "))
            novo_nome = input("Digite o novo nome: ")
            novo_rg = input("Digite o novo RG: ")
            nova_turma = input("Digite a nova turma: ")
            ger.atualizar(id, novo_nome, novo_rg, nova_turma)



        elif opcao == "4":
            try:
                id = int(input("Digite o ID do aluno a remover: "))
                # checar se o ID existe antes de remover
                alunos = ger.listar()
                ids_existentes = [aluno.id for aluno in alunos]

                if id not in ids_existentes:
                    print(f"⚠️ Nenhum aluno encontrado com ID {id}.")
                else:
                    ger.remover(id)
            except ValueError:
                print("⚠️ O ID deve ser um número válido!")

        elif opcao == "5":
            alunos = ger.listar()
            if alunos:
                abrir_lista_presenca(alunos)
            else:
                print("Nenhum aluno cadastrado.")



        elif opcao == "0":
            print("Saindo do sistema...")
            break

        else:
            print("Opção inválida, tente novamente.")

def gerar_relatorio_historico():
    # Criar pasta se não existir
    os.makedirs("Relatorios", exist_ok=True)

    # Data de ontem
    ontem = (date.today() - timedelta(days=1)).isoformat()
    arquivo_excel = f"Relatorios/presenca_{ontem}.xlsx"

    # Buscar alunos
    ger = GerenciadorAlunos()
    alunos = ger.listar()

    # Conectar ao banco para pegar presenças de ontem
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute("SELECT aluno_id, presente FROM presencas WHERE data = ?", (ontem,))
    presencas = dict(cursor.fetchall())
    conn.close()

    # Montar DataFrame com presença
    dados = []
    for i, aluno in enumerate(alunos, start=1):
        dados.append({
            "Nº": i,
            "NOME": aluno.nome,
            "RG": aluno.rg,
            "TURMA": aluno.turma,
            "PRESENTE": "Sim" if presencas.get(aluno.id, 0) == 1 else "Não"
        })

    df = pd.DataFrame(dados)

    # 🔹 Calcular estatísticas
    total = len(df)
    presentes = sum(df["PRESENTE"] == "Sim")
    porcentagem = (presentes / total * 100) if total > 0 else 0

    # 🔹 Adicionar linha extra com resumo
    resumo = pd.DataFrame([{
        "Nº": "",
        "NOME": "Resumo",
        "RG": "",
        "TURMA": "",
        "PRESENTE": f"{presentes}/{total} ({porcentagem:.2f}%)"
    }])

    df_final = pd.concat([df, resumo], ignore_index=True)

    # Salvar no Excel
    df_final.to_excel(arquivo_excel, index=False)

    print(f"✅ Relatório histórico criado: {arquivo_excel}")
