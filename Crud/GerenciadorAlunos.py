import sqlite3
from Classe.Aluno import Aluno

class GerenciadorAlunos:
    def __init__(self, db_name="escola.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._criar_tabela()

    def _criar_tabela(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            rg TEXT,
            turma TEXT
        )
        """)
        self.conn.commit()

    def _normalizar_nome(self, nome):
        return " ".join(nome.strip().split()).upper()

    # CREATE
    def adicionar(self, nome, rg, turma):
        self.cursor.execute(
            "INSERT INTO alunos (nome, rg, turma) VALUES (?, ?, ?)",
            (nome, rg, turma)
        )
        self.conn.commit()

    # READ
    def listar(self):
        self.cursor.execute("SELECT id, nome, rg, turma FROM alunos")
        rows = self.cursor.fetchall()
        return [Aluno(id=row[0], nome=row[1], rg=row[2], turma=row[3]) for row in rows]

    # UPDATE
    def atualizar(self, id, novo_nome, novo_rg, nova_turma):
        novo_nome = self._normalizar_nome(novo_nome)
        self.cursor.execute(
            "UPDATE alunos SET nome = ?, rg = ?, turma = ? WHERE id = ?",
            (novo_nome, novo_rg, nova_turma, id)
        )
        self.conn.commit()

        if self.cursor.rowcount == 0:
            print(f"⚠️ Nenhum aluno encontrado com ID {id}.")
        else:
            print(f"Aluno {id} atualizado para {novo_nome}, RG: {novo_rg}, Turma: {nova_turma}.")

    # DELETE
    def remover(self, id):
        self.cursor.execute("DELETE FROM alunos WHERE id = ?", (id,))
        self.conn.commit()
        print(f"Aluno {id} removido com sucesso!")

    def fechar(self):
        self.conn.close()
