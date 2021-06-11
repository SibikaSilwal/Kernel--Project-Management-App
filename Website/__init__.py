from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser
import os
from flask_login import LoginManager
from flaskext.markdown import Markdown
from flask_ckeditor import CKEditor
from io import BytesIO
from base64 import b64encode

config = configparser.ConfigParser()
path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
config.read(os.path.join(path, 'config.ini'))
connection_string = config['database']['postgres_connection']
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)  # name represents of the file that runs
    app.config['SECRET_KEY'] = 'abbcccdddd'

    Markdown(app)
    # print(connection_string)
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    db.init_app(app)

    from .views import views  # importing blueprint
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    create_database(app)

    login_manager = LoginManager()
    # this means, flask should redirect the not logged in user to login page
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    register_template_filters(flask_app=app)
    ckeditor = CKEditor(app)

    app.jinja_env.globals.update(clever_function=clever_function)
    app.jinja_env.globals.update(Convert_blob_to_base64=Convert_blob_to_base64)

    return app


def create_database(app):
    # if not path.exists('Website/' + )
    db.create_all(app=app)
    print("New database created")


def register_template_filters(flask_app: Flask) -> None:
    from . import custom_template_filters
    flask_app.register_blueprint(custom_template_filters.blueprint)
    return None


def clever_function(name):
    if(len(name) == 0):
        return
    initials = name[0].upper()
    for i in range(1, len(name) - 1):
        if (name[i] == ' '):
            initials = initials + (name[i + 1].upper())
    return initials


def Convert_blob_to_base64(file):
    return b64encode(file).decode("utf-8")
