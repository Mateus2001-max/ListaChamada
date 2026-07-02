class Aluno:
    def __init__(self, id, nome, rg=None, turma=None):
        self.id = id
        self.nome = nome
        self.rg = rg
        self.turma = turma

    def __str__(self):
        return f"{self.id} - {self.nome} | RG: {self.rg} | Turma: {self.turma}"
