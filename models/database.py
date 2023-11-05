from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cursos(db.Model):
    __tablename__ = 'cursos'  # Nome da tabela no banco de dados

    IDCurso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Titulo = db.Column(db.String(255), nullable=False, unique=True)  # Coluna para o título (texto com até 255 caracteres)
    Nivel = db.Column(db.String(50), nullable=False)   # Coluna para o nível (texto com até 50 caracteres)

    def __init__(self, Titulo, Nivel):
        self.Titulo = Titulo
        self.Nivel = Nivel


class Professores(db.Model):
    __tablename__ = 'professores'  # Nome da tabela no banco de dados

    IDProfessor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nome = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), nullable=False, unique=True)

    def __init__(self, Nome, Email):
        self.Nome = Nome
        self.Email = Email

class Materias(db.Model):
    __tablename__ = 'materias'  # Nome da tabela no banco de dados

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