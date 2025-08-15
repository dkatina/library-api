from flask import Flask
from .models import db
from .extensions import ma
from .blueprints.users import users_bp


def create_app(config_name):

    app = Flask(__name__) #Creating base app
    app.config.from_object(f'config.{config_name}')


    #initialize extensions (plugging them in)
    db.init_app(app)
    ma.init_app(app)

    #Register blueprints
    app.register_blueprint(users_bp, url_prefix='/users')

    return app