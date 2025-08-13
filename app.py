from datetime import date
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, String

app = Flask(__name__) #Instatiating our Flask app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' #Connecting a sqlite db to our flask app


#Create a base class for our models
class Base(DeclarativeBase):
    pass
    #could add your own config


#Instatiate your SQLAlchemy database:

db = SQLAlchemy(model_class = Base)

#Initialize my extension onto my Flask app

db.init_app(app) #adding the db to the app.


class Users(Base):
    __tablename__ = 'users' #lowercase plural form of resource

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    DOB: Mapped[date] = mapped_column(Date, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)



with app.app_context():
    db.create_all() #Creating our database tables


app.run()