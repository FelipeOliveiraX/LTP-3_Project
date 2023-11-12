import sys
sys.path.append('..')
from app import app, db
from database import Cursos, Professores, Materias, Avaliacoes

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
    # novo_materia = Materias(Titulo="Banco de Dados I", Periodo=3, IDCurso=1, IDProfessor=1)
    # db.session.add(novo_materia)
    # db.session.commit()

    # # DELETAR MATERIA ERRADA
    # materia_excluir = Materias.query.filter_by(IDMateria=3).first()

    # if materia_excluir:
    #     # Exclua a matéria
    #     db.session.delete(materia_excluir)
    #     db.session.commit()
    #     print("Matéria com IDMateria 3 excluída com sucesso.")
    # else:
    #     print("Matéria com IDMateria 3 não encontrada.")


