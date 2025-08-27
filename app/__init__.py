from flask import Flask
from .models import db
from .extensions import ma, limiter, cache
from .blueprints.users import users_bp
from .blueprints.books import books_bp
from .blueprints.loans import loans_bp
from .blueprints.orders import orders_bp
from .blueprints.items import items_bp
from flask_swagger_ui import get_swaggerui_blueprint #need to create a blueprint to plug into our app

SWAGGER_URL = '/api/docs' #Url for exposing my swagger ui
API_URL = '/static/swagger.yaml'


#creating swagger blueprint
swagger_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': 'Library Management API'} )


def create_app(config_name): #Application Factory

    app = Flask(__name__) #Creating base app
    app.config.from_object(f'config.{config_name}')


    #initialize extensions (plugging them in)
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    #Register blueprints
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(loans_bp, url_prefix='/loans')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(items_bp, url_prefix='/items')
    app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL) #Registering my Swagger blueprint to make it accessible on my app.

    return app