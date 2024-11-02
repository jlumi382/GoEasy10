from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from .utils import categories, create_dirs

db = SQLAlchemy()
DB_NAME =  'database.db'

def create_app():
    app = Flask(__name__, template_folder="templates/")
    app.config['SESSION_PERMANENT'] = False
    app.secret_key = getenv("SECRET_KEY")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(app.root_path, DB_NAME)}'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager
    from .views import views
    from .auth import auth
    from .admin import admin


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('static', 'favicon.ico')

    from . import models as models

    create_database(app)

    with app.app_context():
        create_dirs()
        for category in categories:
            add_category(models.Category, category)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists(path.join(app.root_path, DB_NAME)):
        with app.app_context():
            db.create_all()

def add_category(CategoryModel, category_name):
    existing_category = CategoryModel.query.filter_by(name=category_name).first()
    
    if not existing_category:
        new_category = CategoryModel(name=category_name, short_name=category_name.lower())
        db.session.add(new_category)
        db.session.commit()
