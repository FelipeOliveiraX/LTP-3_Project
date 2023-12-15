# -------------------------  IMPORTAÇÕES  -----------------------------------------------------
from flask import Flask, url_for, session, redirect, render_template, request # funções básicas do Flask
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user # Flask-Login e suas funções
from authlib.integrations.flask_client import OAuth # integração do flask logincom o oauth do Google
from flask_sqlalchemy import SQLAlchemy # SQLAlchemy 
from sqlalchemy.exc import IntegrityError # tratamento para erro na integração com o banco
from sqlalchemy import func # funções do SQLAlchemy
from models.database import db, Cursos, Materias, Professores, Avaliacoes # classes do banco de dados (conforme SQLAlchemy)
from collections import defaultdict # tratamento de dados importados do banco

# -------------------------  START FLASK  -----------------------------------------------------
# configurações básicas para início do Flask
app = Flask(__name__, template_folder='templates')
app.debug = True
app.secret_key = 'really_secret'
# ---------------------------------------------------------------------------------------------

# -------------------------  DATABASE CONFIG  -------------------------------------------------
# configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# ---------------------------------------------------------------------------------------------

# -------------------------  OAUTH CONFIG  ----------------------------------------------------
# configurações da autenticação Google
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
# starter do Flask Login
login_manager = LoginManager(app)
login_manager.login_view = 'not_logged'

# cria uma instância de User com base no user_id 
@login_manager.user_loader
def load_user(user_id):       
    user = User(user_id)
    return user

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
# ---------------------------------------------------------------------------------------------

# -------------------------  ROUTES  ----------------------------------------------------------
# rota principal
@app.route("/")
@login_required
def hello_world():
    name = dict(session).get('name', None) # recupera o nome da pessoa logada para exibir
    return render_template('index.html', name=name) 

# rota intermediária para login (sem template)
@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

# rota do login Google (sem template)
@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')    
    user_info = resp.json()
    email = user_info.get('email', '') # armazena o email da usado, para verificação   

    if email.endswith('@estudante.ifto.edu.br') or Professores.query.filter_by(Email=email).first(): # verifica se o e-mail termina com "@estudante.ifto.edu.br" ou é de algum professor        
        user = User(email) # cria uma instância do usuário e faz o login
        login_user(user) # inicia a sessão       
        session['name'] = user_info.get('name', None) # armazena o nome na sessão
        session['email'] = email # armazena o email na sessão  
        return redirect('/') # redireciona para a página inicial
    else: # se o e-mail não atender aos critérios, redireciona para uma página de erro        
        return render_template('error.html', error_message='Apenas usuários institucionais e autorizados são permitidos.')

# rota da página de usuário não logado
@app.route("/not_logged")
def not_logged():
    return render_template('not_logged.html')  

# rota de logout (sem template)
@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key) # limpa a sessão
    return redirect('/') 

# rota dos cursos
@app.route('/cursos')
@login_required
def cursos():
    cursos = Cursos.query.all() # buscar os dados dos cursos no banco    
    cursos_por_nivel = defaultdict(list) # organiza os cursos em um dicionário, agrupados por nível (Médio ou Superior) 

    for curso in cursos: # insere os cursos no dicionário
        cursos_por_nivel[curso.Nivel].append(curso)

    return render_template('cursos.html', cursos_por_nivel=cursos_por_nivel)    

# rota das materias
@app.route('/cursos/<path:curso_titulo>', methods=['POST'])
@login_required
def materias(curso_titulo):
    id_curso = request.form.get('id_curso') # recebe o IDCurso passado pela página anterior
    curso = Cursos.query.get(id_curso) # busca qual o curso, baseado no IDCurso  
    materias = Materias.query.filter_by(IDCurso=id_curso).all() # recupera as matérias relacionadas a este curso com base no IDCurso
    print(curso.Titulo)
    # carrega o nome do professor para cada matéria
    for materia in materias:
        professor = Professores.query.get(materia.IDProfessor)
        materia.professor_nome = professor.Nome

    # agrupa as matérias por período
    materias_por_periodo = defaultdict(list)
    for materia in materias:
        materias_por_periodo[materia.Periodo].append(materia)

    return render_template('materias.html', curso=curso, materias_por_periodo=dict(materias_por_periodo), materias=materias)

# rota das avaliações
@app.route('/avaliacao', methods=['POST'])
@login_required
def avaliacao():
    # recebe os dados passados pela página anterior:
    id_materia = request.form.get('id_materia') 
    id_professor = request.form.get('id_professor')
    materia_nome = request.form.get('materia_nome')
    professor_nome = request.form.get('professor_nome')
    session['email'] = session.get('email', None) # recupera o email da sessão
    print(f'id_materia: {id_materia}, id_professor: {id_professor}, materia_nome: {materia_nome}, professor_nome: {professor_nome}') # teste do que está sendo recebido
    return render_template('avaliacao.html',
                           id_materia=id_materia,
                           id_professor=id_professor,
                           materia_nome=materia_nome,
                           professor_nome=professor_nome)

# rota para salvar a avaliação (sem template)
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
        return render_template('approve.html', approve_message='Avaliação feita com sucesso!')
    except IntegrityError:
        db.session.rollback()        
        return render_template('error.html', error_message='Essa avaliação já foi feita! Cada aluno só pode ter uma avaliação por disciplina.')        

# rota dos resultados (para selecionar o professor apenas)  
@app.route('/resultados')
@login_required
def listar_professores():    
    professores_em_ordem = Professores.query.order_by(Professores.Nome).all() # recupera a lista de professores em ordem alfabética    
    return render_template('resultados.html', professores=professores_em_ordem)

# rota dos resultados (para exibir o relatório do professor selecionado)  
@app.route('/resultados/<path:professor_nome>', methods=['POST'])
@login_required
def exibir_avaliacoes_professor(professor_nome):    
    professor = Professores.query.filter_by(Nome=professor_nome).first() # recupera os dados do professor pelo nome

    # consulta para calcular a média das avaliações, agrupadas por matéria   
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
    
    media_por_materia = [] # para armazenar os resultados

    for resultado in resultados_query:
        # calcula a soma das médias e divide por 2:
        media_total = round((resultado.media_nota1 + resultado.media_nota2 + resultado.media_nota3 +
                        resultado.media_nota4 + resultado.media_nota5 + resultado.media_nota6) / 2, 2)
        
        # adiciona as informações à lista de dicionários
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
    
    if not media_por_materia: # se não houver avaliações para o professor        
        return render_template('error.html', error_message='O professor(a) ainda não foi avaliado!')
     
    media_das_medias = round(sum(materia['media_total'] for materia in media_por_materia) / len(media_por_materia), 2) # calcula a média das médias, para dar a nota final
    return render_template('resultados_prof.html', professor=professor, media_por_materia=media_por_materia, media_das_medias=media_das_medias)
# ---------------------------------------------------------------------------------------------
  

