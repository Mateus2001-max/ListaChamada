import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sqlite3
from datetime import date

def abrir_lista_presenca(alunos):
    root = tk.Tk()
    root.title("Lista de Presença")

    # Cabeçalho
    ttk.Label(root, text="ALUNO", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5)
    ttk.Label(root, text="RG", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, pady=5)
    ttk.Label(root, text="TURMA", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, pady=5)
    ttk.Label(root, text="PRESENTE", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=10, pady=5)
    ttk.Label(root, text="AÇÕES", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=10, pady=5)

    checks = []
    hoje = date.today().isoformat()

    # 🔹 Carregar presenças salvas do banco
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute("SELECT aluno_id, presente FROM presencas WHERE data = ?", (hoje,))
    presencas = dict(cursor.fetchall())
    conn.close()

    def calcular():
        presentes = sum(var.get() for var in checks)
        total = len(alunos)
        porcentagem = (presentes / total) * 100 if total > 0 else 0
        resultado.config(text=f"Presentes: {presentes}/{total} ({porcentagem:.2f}%)")

    def salvar_presenca():
        conn = sqlite3.connect("escola.db")
        cursor = conn.cursor()
        for aluno, var in zip(alunos, checks):
            presente = 1 if var.get() else 0
            cursor.execute("""
                INSERT INTO presencas (aluno_id, data, presente)
                VALUES (?, ?, ?)
                ON CONFLICT(aluno_id, data) DO UPDATE SET presente=excluded.presente
            """, (aluno.id, hoje, presente))
        conn.commit()
        conn.close()
        resultado.config(text="Presença salva com sucesso!")

    def editar_aluno(aluno):
        novo_nome = simpledialog.askstring("Editar Aluno", "Novo nome:", initialvalue=aluno.nome)
        novo_rg = simpledialog.askstring("Editar Aluno", "Novo RG:", initialvalue=aluno.rg)
        nova_turma = simpledialog.askstring("Editar Aluno", "Nova Turma:", initialvalue=aluno.turma)
        if novo_nome and novo_rg and nova_turma:
            conn = sqlite3.connect("escola.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE alunos SET nome=?, rg=?, turma=? WHERE id=?",
                           (novo_nome, novo_rg, nova_turma, aluno.id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Aluno atualizado!")
            root.destroy()
            from Crud.GerenciadorAlunos import GerenciadorAlunos
            abrir_lista_presenca(GerenciadorAlunos().listar())

    def excluir_aluno(aluno):
        if messagebox.askyesno("Confirmar", f"Excluir {aluno.nome}?"):
            conn = sqlite3.connect("escola.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alunos WHERE id=?", (aluno.id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Aluno excluído!")
            root.destroy()
            abrir_lista_presenca([a for a in alunos if a.id != aluno.id])

    def adicionar_aluno():
        nome = simpledialog.askstring("Novo Aluno", "Nome:")
        rg = simpledialog.askstring("Novo Aluno", "RG:")
        turma = simpledialog.askstring("Novo Aluno", "Turma:")
        if nome and rg and turma:
            conn = sqlite3.connect("escola.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alunos (nome, rg, turma) VALUES (?, ?, ?)", (nome, rg, turma))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Aluno adicionado!")
            root.destroy()
            from Crud.GerenciadorAlunos import GerenciadorAlunos
            abrir_lista_presenca(GerenciadorAlunos().listar())

    # 🔹 Criar linhas de alunos
    for i, aluno in enumerate(alunos, start=1):
        ttk.Label(root, text=aluno.nome).grid(row=i, column=0, padx=10, pady=5)
        ttk.Label(root, text=aluno.rg).grid(row=i, column=1, padx=10, pady=5)
        ttk.Label(root, text=aluno.turma).grid(row=i, column=2, padx=10, pady=5)

        var = tk.BooleanVar(value=bool(presencas.get(aluno.id, 0)))
        chk = ttk.Checkbutton(root, variable=var, command=calcular)
        chk.grid(row=i, column=3)
        checks.append(var)

        ttk.Button(root, text="Editar", command=lambda a=aluno: editar_aluno(a)).grid(row=i, column=4, padx=5)
        ttk.Button(root, text="Excluir", command=lambda a=aluno: excluir_aluno(a)).grid(row=i, column=5, padx=5)

    resultado = ttk.Label(root, text="")
    resultado.grid(row=len(alunos)+1, column=0, columnspan=6)

    ttk.Button(root, text="Salvar Presença", command=salvar_presenca).grid(row=len(alunos)+2, column=0, columnspan=6, pady=10)
    ttk.Button(root, text="Adicionar Aluno", command=adicionar_aluno).grid(row=len(alunos)+3, column=0, columnspan=6, pady=10)

    calcular()
    root.mainloop()
