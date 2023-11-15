from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

# ---------------------------------------------------------------------------------------
class Cursos(db.Model):
    __tablename__ = 'cursos'  # Nome da tabela no banco de dados

    IDCurso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(255), nullable=False, unique=True)  
    Nivel = db.Column(db.String(50), nullable=False)   

    def __init__(self, Titulo, Nivel):
        self.Titulo = Titulo
        self.Nivel = Nivel
# ---------------------------------------------------------------------------------------
class Professores(db.Model):
    __tablename__ = 'professores'  

    IDProfessor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nome = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, Nome, Email):
        self.Nome = Nome
        self.Email = Email
# ---------------------------------------------------------------------------------------
class Materias(db.Model):
    __tablename__ = 'materias'  

    IDMateria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(255), nullable=False)
    Periodo = db.Column(db.Integer, nullable=False)
    IDCurso = db.Column(db.Integer, nullable=False)
    IDProfessor = db.Column(db.Integer, nullable=False)

    def __init__(self, Titulo, Periodo, IDCurso, IDProfessor):
        self.Titulo = Titulo
        self.Periodo = Periodo
        self.IDCurso = IDCurso
        self.IDProfessor = IDProfessor
# ---------------------------------------------------------------------------------------
class Avaliacoes(db.Model):
    __tablename__ = 'avaliacoes'

    IDAvaliacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IDMateria = db.Column(db.Integer, nullable=False)
    IDProfessor = db.Column(db.Integer, nullable=False)
    EmailAluno = db.Column(db.String(255), nullable=False)
    Nota1 = db.Column(db.Float, nullable=False)
    Nota2 = db.Column(db.Float, nullable=False)
    Nota3 = db.Column(db.Float, nullable=False)
    Nota4 = db.Column(db.Float, nullable=False)
    Nota5 = db.Column(db.Float, nullable=False)
    Nota6 = db.Column(db.Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('IDMateria', 'EmailAluno', name='uq_idmateria_emailaluno'),
    )

    def __init__(self, IDMateria, IDProfessor, EmailAluno, Nota1, Nota2, Nota3, Nota4, Nota5, Nota6):
        self.IDMateria = IDMateria
        self.IDProfessor = IDProfessor
        self.EmailAluno = EmailAluno
        self.Nota1 = Nota1
        self.Nota2 = Nota2
        self.Nota3 = Nota3
        self.Nota4 = Nota4     
        self.Nota5 = Nota5
        self.Nota6 = Nota6    
# ---------------------------------------------------------------------------------------