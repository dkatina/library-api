from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Table, Column
from datetime import datetime, timedelta, date

#Create a base class for our models
class Base(DeclarativeBase):
    pass
    #could add your own config


#Instatiate your SQLAlchemy database:
db = SQLAlchemy(model_class = Base)


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
    password: Mapped[str] = mapped_column(String(500), nullable=False)
    DOB: Mapped[date] = mapped_column(Date, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)

    #One to Many relationship from User to Books
    loans: Mapped[list['Loans']] = relationship('Loans', back_populates='user')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='user')

  
class Loans(Base):
    __tablename__ = 'loans'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    loan_date: Mapped[date] = mapped_column(Date, default=datetime.now())
    deadline: Mapped[date] = mapped_column(Date, default=datetime.now() + timedelta(days=14))
    return_date: Mapped[date] = mapped_column(Date, nullable=True)

    #Relationships
    user: Mapped['Users'] = relationship('Users', back_populates='loans')
    books: Mapped[list['Books']] = relationship("Books", secondary=loan_books, back_populates='loans') #Many to Many relationship going through the loan_books table
   

class Books(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    genre: Mapped[str] = mapped_column(String(360), nullable=False)
    age_category: Mapped[str] = mapped_column(String(120), nullable=False)
    publish_date: Mapped[date] = mapped_column(Date, nullable=False)
    author: Mapped[str] = mapped_column(String(500), nullable=False)

    #Relationship
    loans: Mapped[list['Loans']] = relationship('Loans', secondary=loan_books, back_populates='books')

class Orders(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=True)
    #submitted default == False until the order was submitted changed to True

    user: Mapped['Users'] = relationship('Users', back_populates='orders')
    items: Mapped[list['Items']] = relationship('Items', back_populates='order')

class ItemDescriptions(Base):
    __tablename__ = 'item_descriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    item_name: Mapped[str] = mapped_column(String(225), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    items: Mapped[list['Items']] = relationship('Items', back_populates='item_description')

class Items(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    desc_id: Mapped[int] = mapped_column(ForeignKey('item_descriptions.id'), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=True)

    order: Mapped['Orders'] = relationship('Orders', back_populates='items')
    item_description: Mapped['ItemDescriptions'] = relationship('ItemDescriptions', back_populates='items')
