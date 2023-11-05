import sys
sys.path.append('..')
from app import app, db
from database import Cursos, Professores, Materias

with app.app_context():

    db.create_all()

    # Insere Curso
    # novo_curso = Cursos(Titulo="Técnico em Meio Ambiente", Nivel="Médio")
    # db.session.add(novo_curso)
    
    # cursos_a_inserir = [
    # Cursos(Titulo="Técnico em Meio Ambiente", Nivel="Médio"),
    # Cursos(Titulo="Administração", Nivel="Superior"),
    # Cursos(Titulo="Licenciatura em Matemática", Nivel="Superior"),
    # Cursos(Titulo="Licenciatura em Química", Nivel="Superior"),
    # Cursos(Titulo="Tecnologia em Alimentos", Nivel="Superior"),
    # ]
    # db.session.add_all(cursos_a_inserir)
    # db.session.commit()

    # Insere Professor
    # novo_professor = Professores(Nome="Felipe Oliveira", Email="joeltonfelipeos@gmail.com")
    # db.session.add(novo_professor)
    # db.session.commit()

    # Insere Matéria
    # novo_materia = Materias(Titulo="Matemática Discreta", Periodo=2, IDCurso=1, IDProfessor=1)
    # db.session.add(novo_materia)
    # db.session.commit()
