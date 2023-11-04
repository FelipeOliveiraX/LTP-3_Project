from flask import Flask, url_for, redirect, session, render_template
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
from models.database import db, Cursos, Materias, Professores
from collections import defaultdict


# -------------------------  START FLASK  -----------------------------------------------------
app = Flask(__name__, template_folder='templates')
app.debug = True
app.secret_key = 'really_secret'
# ---------------------------------------------------------------------------------------------

# -------------------------  DATABASE CONFIG  -------------------------------------------------
# Configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
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
login_manager.login_view = 'not_logged_in'

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
    return f'Olá, seja bem-vindo(a) {name}!'"<a href='/logout'><button>Logout</button></a>"    

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
    # Cria uma instância do usuário e faz o login
    user = User(user_info['email'])
    login_user(user)
    # Armazene o nome na sessão
    session['name'] = user_info.get('name', None)     
    return redirect('/')

# rota temporária da página de usuário não logado, melhorar futuramente
@app.route("/not_logged_in")
def not_logged_in():
    return f'Você não está logado. Clique aqui para fazer login -->'"<a href='/login'><button>Login</button></a>"  

# rota de logout (não precisa de template)
@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

# rota de para exibir pesquisa no banco
@app.route('/cursos')
def cursos():
    cursos = Cursos.query.all()
     # Organize os cursos em um dicionário onde a chave é o nível e o valor é uma lista de cursos daquele nível
    cursos_por_nivel = defaultdict(list)

    for curso in cursos:
        cursos_por_nivel[curso.Nivel].append(curso)

    return render_template('cursos.html', cursos_por_nivel=cursos_por_nivel)
    # return render_template('banco.html', cursos=cursos)

@app.route('/cursos/<int:curso_id>')
def materias(curso_id):
    curso = Cursos.query.get(curso_id)
    # Recupere as matérias relacionadas a este curso com base na coluna IDCurso
    materias = Materias.query.filter_by(IDCurso=curso_id).all()

    # Carregue o nome do professor para cada matéria
    for materia in materias:
        professor = Professores.query.get(materia.IDProfessor)
        materia.professor_nome = professor.Nome

    return render_template('materias.html', curso=curso, materias=materias)
# ---------------------------------------------------------------------------------------------
  

