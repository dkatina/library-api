

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True

class TestingConfig:
    pass

class ProductionConfig:
    pass