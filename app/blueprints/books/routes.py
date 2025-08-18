
from . import books_bp
from .schemas import book_schema, books_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Books, db

#Create Book Endpoint
@books_bp.route('', methods=['POST'])
def create_book():
    try:
        data = book_schema.load(request.json) #validates data and translates json object to python dictionary
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_book = Books(**data)
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book), 201


#READ BOOKS
@books_bp.route('', methods=['GET'])
def get_books():
    books = db.session.query(Books).all()
    return books_schema.jsonify(books), 200


#UPDATE BOOK
@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = db.session.get(Books, book_id)

    if not book:
        return jsonify("Invalid book_id"), 404
    
    try:
        data = book_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in data.items():
        setattr(book, key, value) #setting my new attributes

    db.session.commit()
    return book_schema.jsonify(book), 200


#DELETE BOOK
@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = db.session.get(Books,book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify(f"Successfully deleted book {book_id}")