from datetime import date
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Date, ForeignKey, String, Table, Column
from flask_marshmallow import Marshmallow #Importing marshmallow class
from marshmallow import ValidationError #Errors that are produced from our schema are called Validation errors

app = Flask(__name__) #Instatiating our Flask app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' #Connecting a sqlite db to our flask app


#Create a base class for our models
class Base(DeclarativeBase):
    pass
    #could add your own config


#Instatiate your SQLAlchemy database:

db = SQLAlchemy(model_class = Base)
ma = Marshmallow()

#Initialize my extension onto my Flask app

db.init_app(app) #adding the db to the app.
ma.init_app(app)

loan_books = Table(
    'loan_books',
    Base.metadata,
    Column('loan_id', ForeignKey('loans.id')),
    Column('book_id', ForeignKey('books.id'))
)


class Users(Base):
    __tablename__ = 'users' #lowercase plural form of resource

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    DOB: Mapped[date] = mapped_column(Date, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)

    #One to Many relationship from User to Books
    loans: Mapped[list['Loans']] = relationship('Loans', back_populates='user')

  
class Loans(Base):
    __tablename__ = 'loans'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    loan_date: Mapped[date] = mapped_column(Date, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=True)
    return_date: Mapped[date] = mapped_column(Date, nullable=True)

    #Relationships
    user: Mapped['Users'] = relationship('Users', back_populates='loans')
    books: Mapped[list['Books']] = relationship("Books", secondary=loan_books, back_populates='loans') #Many to Many relationship going through the loan_books table
   

class Books(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    genre: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    age_category: Mapped[str] = mapped_column(String(120), nullable=False)
    publish_date: Mapped[date] = mapped_column(Date, nullable=True)
    author: Mapped[str] = mapped_column(String(500), nullable=True)

    #Relationship
    loans: Mapped[list['Loans']] = relationship('Loans', secondary=loan_books, back_populates='books')


#Install Marshmellow
#pip install flask-marshmallow marshmallow-sqlalchemy

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users #Creates a schema that validates the data as defined by our Users Model

user_schema = UserSchema() #Creating an instance of my schema that I can actually use to validate, deserialize, and serialze JSON
users_schema = UserSchema(many=True) #Allows this schema to translate a list of User objects all at once

#=========================================== CRUD for Users =========================================

#CREATE USER ROUTE
@app.route('/users', methods=['POST']) #route servers as the trigger for the function below.
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    

    new_user = Users(**data) #Creating User object
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

#Read Users
@app.route('/users', methods=['GET']) #Endpoint to get user information
def read_users():
    users = db.session.query(Users).all()
    return users_schema.jsonify(users), 200


#Read Individual User - Using a Dynamic Endpoint
@app.route('/users/<int:user_id>', methods=['GET'])
def read_user(user_id):
    user = db.session.get(Users, user_id)
    return user_schema.jsonify(user), 200


#Delete a User
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.session.get(Users, user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted user {user_id}"}), 200


#Update a User
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    pass
#Query the user by id
#Validate and Deserialze the updates that they are sending in the body of the request
#for each of the values that they are sending, we will change the value of the queried object
#commit the changes
#return a response

    




with app.app_context():
    db.create_all() #Creating our database tables


app.run(debug=True)