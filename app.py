from flask import Flask, url_for, session, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from models.database import db, Cursos, Materias, Professores, Avaliacoes
from collections import defaultdict

# -------------------------  START FLASK  -----------------------------------------------------
app = Flask(__name__, template_folder='templates')
app.debug = True
app.secret_key = 'really_secret'
# ---------------------------------------------------------------------------------------------

# -------------------------  DATABASE CONFIG  -------------------------------------------------
# Configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# ---------------------------------------------------------------------------------------------

# -------------------------  OAUTH CONFIG  ----------------------------------------------------
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='612248981422-j61ue92ug9kflfk3dqkf29l2fnsmg083.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',    
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)
# ---------------------------------------------------------------------------------------------

# -------------------------  FLASK LOGIN  -----------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'not_logged'

@login_manager.user_loader
def load_user(user_id):
    # Cria uma instância de User com base no user_id
    # ALTERAR PARA COMPARAR COM O BANCO OU O @ IFTO
    user = User(user_id)
    return user

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
# ---------------------------------------------------------------------------------------------

# -------------------------  ROUTES  ----------------------------------------------------------
# main route
@app.route("/")
@login_required
def hello_world():
    name = dict(session).get('name', None)
    return render_template('index.html', name=name) 

# rota intermediária para login (não precisa de template)
@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

# rota do google login (não precisa de template)
@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')    
    user_info = resp.json()
    
    # Verifica se o e-mail termina com "@estudante.ifto.edu.br"
    if user_info.get('email', '').endswith('@estudante.ifto.edu.br'):
        # Cria uma instância do usuário e faz o login
        user = User(user_info['email'])
        login_user(user)
        # Armazene o nome e email na sessão
        session['name'] = user_info.get('name', None) 
        session['email'] = user_info.get('email', None)    
        return redirect('/')
    else:
        # Se o e-mail não atender aos critérios, redirecione para uma página de erro
        return render_template('error.html', error_message='Apenas e-mails institucionais são permitidos.')

# rota temporária da página de usuário não logado, melhorar futuramente
@app.route("/not_logged")
def not_logged():
    return render_template('not_logged.html')  

# rota de logout (não precisa de template)
@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

# rota dos cursos
@app.route('/cursos')
@login_required
def cursos():
    cursos = Cursos.query.all()
     # Organize os cursos em um dicionário onde a chave é o nível e o valor é uma lista de cursos daquele nível
    cursos_por_nivel = defaultdict(list)

    for curso in cursos:
        cursos_por_nivel[curso.Nivel].append(curso)

    return render_template('cursos.html', cursos_por_nivel=cursos_por_nivel)
    # return render_template('banco.html', cursos=cursos)

# rota das materias
@app.route('/cursos/<path:curso_titulo>', methods=['POST'])
@login_required
def materias(curso_titulo):
    id_curso = request.form.get('id_curso')
    curso = Cursos.query.get(id_curso)

    # Recupera as matérias relacionadas a este curso com base no IDCurso
    materias = Materias.query.filter_by(IDCurso=id_curso).all()

    # Carregua o nome do professor para cada matéria
    for materia in materias:
        professor = Professores.query.get(materia.IDProfessor)
        materia.professor_nome = professor.Nome

    # Agrupa as matérias por período
    materias_por_periodo = defaultdict(list)
    for materia in materias:
        materias_por_periodo[materia.Periodo].append(materia)

    return render_template('materias.html', curso=curso, materias_por_periodo=dict(materias_por_periodo), materias=materias)

@app.route('/avaliacao', methods=['POST'])
@login_required
def avaliacao():
    id_materia = request.form.get('id_materia')
    id_professor = request.form.get('id_professor')
    materia_nome = request.form.get('materia_nome')
    professor_nome = request.form.get('professor_nome')
    session['email'] = session.get('email', None)
    print(f'id_materia: {id_materia}, id_professor: {id_professor}, materia_nome: {materia_nome}, professor_nome: {professor_nome}')
    return render_template('avaliacao.html',
                           id_materia=id_materia,
                           id_professor=id_professor,
                           materia_nome=materia_nome,
                           professor_nome=professor_nome)

@app.route('/salvar_avaliacao', methods=['POST'])
@login_required
def salvar_avaliacao():
    try:
        print(request.form)
        nova_avaliacao = Avaliacoes(
            IDMateria=request.form['IDMateria'],
            IDProfessor=request.form['IDProfessor'],
            EmailAluno=request.form['EmailAluno'],
            Nota1=request.form['Nota1'],
            Nota2=request.form['Nota2'],
            Nota3=request.form['Nota3'],
            Nota4=request.form['Nota4'],
            Nota5=request.form['Nota5'],
            Nota6=request.form['Nota6']
        )
        db.session.add(nova_avaliacao)
        db.session.commit()
        return 'Avaliação adicionada com sucesso!'
    except IntegrityError:
        db.session.rollback()
        return render_template('error.html', error_message='Avaliação duplicada. Cada aluno só pode ter uma avaliação por matéria.')        
    
@app.route('/resultados')
@login_required
def listar_professores():
    # Recupera a lista de professores em ordem alfabética
    professores_em_ordem = Professores.query.order_by(Professores.Nome).all()
    
    return render_template('resultados.html', professores=professores_em_ordem)

@app.route('/resultados/<path:professor_nome>', methods=['POST'])
@login_required
def exibir_avaliacoes_professor(professor_nome):
    # Recupera o professor pelo nome
    professor = Professores.query.filter_by(Nome=professor_nome).first()

    # Consulta para calcular a média das avaliações agrupadas por matéria   
    resultados_query = db.session.query(
        Materias.Titulo,
        func.avg(Avaliacoes.Nota1).label('media_nota1'),
        func.avg(Avaliacoes.Nota2).label('media_nota2'),
        func.avg(Avaliacoes.Nota3).label('media_nota3'),
        func.avg(Avaliacoes.Nota4).label('media_nota4'),
        func.avg(Avaliacoes.Nota5).label('media_nota5'),
        func.avg(Avaliacoes.Nota6).label('media_nota6')
    ).join(Avaliacoes, Materias.IDMateria == Avaliacoes.IDMateria) \
    .filter(Avaliacoes.IDProfessor == professor.IDProfessor) \
    .group_by(Materias.Titulo).all()

    # Criar uma lista de dicionários para armazenar os resultados
    media_por_materia = []
    for resultado in resultados_query:
        # Calcule a soma das médias e divida por 2
        media_total = round((resultado.media_nota1 + resultado.media_nota2 + resultado.media_nota3 +
                        resultado.media_nota4 + resultado.media_nota5 + resultado.media_nota6) / 2, 2)
        # Adicione as informações à lista de dicionários
        media_por_materia.append({
            'TituloMateria': resultado.Titulo,
            'media_nota1': resultado.media_nota1,
            'media_nota2': resultado.media_nota2,
            'media_nota3': resultado.media_nota3,
            'media_nota4': resultado.media_nota4,
            'media_nota5': resultado.media_nota5,
            'media_nota6': resultado.media_nota6,
            'media_total': media_total
        })
    # Calcule a média das médias totais
    media_das_medias = round(sum(materia['media_total'] for materia in media_por_materia) / len(media_por_materia), 2)
    print(media_das_medias)
    # Renderize o template HTML com as médias das avaliações por matéria
    return render_template('resultados_prof.html', professor=professor, media_por_materia=media_por_materia, media_das_medias=media_das_medias)
# ---------------------------------------------------------------------------------------------
  

