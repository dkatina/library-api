from flask import Flask
from .models import db
from .extensions import ma
from .blueprints.users import users_bp
from .blueprints.books import books_bp
from .blueprints.loans import loans_bp


def create_app(config_name):

    app = Flask(__name__) #Creating base app
    app.config.from_object(f'config.{config_name}')


    #initialize extensions (plugging them in)
    db.init_app(app)
    ma.init_app(app)

    #Register blueprints
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(loans_bp, url_prefix='/loans')

    return app