
from app.util.auth import admin_required
from . import books_bp
from .schemas import book_schema, books_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Books, db
from app.extensions import limiter, cache
from sqlalchemy import select

#Create Book Endpoint
@books_bp.route('', methods=['POST'])
@admin_required
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
@cache.cached(timeout=30) #If you cache paginated routes it will cache a single page, and continue to serve that page until the cache refreshes (Somthing to think about)
def get_books():
    try:
        page = int(request.args.get('page')) #Converting str nums into ints
        per_page = int(request.args.get('per_page')) 
        query = select(Books)
        books = db.paginate(query, page=page, per_page=per_page) # Handles our pagination so we don't have to track how many items to be sending/
        return books_schema.jsonify(books), 200
    except: #Defaulting to our regular query if they dont send a page or page number
        books = db.session.query(Books).all()
        return books_schema.jsonify(books), 200


#UPDATE BOOK
@books_bp.route('/<int:book_id>', methods=['PUT'])
@limiter.limit("30 per hour")
def update_book(book_id):
    book = db.session.get(Books, book_id) #

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
@limiter.limit("8 per day")
def delete_book(book_id):
    book = db.session.get(Books,book_id) # .get is only for querying with a primary key
    db.session.delete(book)
    db.session.commit()
    return jsonify(f"Successfully deleted book {book_id}")



@books_bp.route('/popularity', methods=['GET'])
def get_popular_books():

    books = db.session.query(Books).all() #Grabbing all books

    #Sort books list based off of how many loans they've been apart of.
    books.sort(key= lambda book: len(book.loans), reverse=True) #Reversing to get the most popular books first

    output = []
    for book in books[:5]: #For each book
        book_format = {
            "book": book_schema.dump(book), #translate the book to json
            "readers": len(book.loans) #add the amount of readers
        }
        output.append(book_format) #append this dictionary to an output list

    return jsonify(output), 200 #jsonify the output list


@books_bp.route('/search', methods=['GET'])
def search_book():
    title = request.args.get('title') #Accessing the query paramters from my URL

    books = db.session.query(Books).where(Books.title.ilike(f"%{title}%")).all() #Searching for a books whos title contains the title we got from the query parameter

    return books_schema.jsonify(books), 200












#.sort(key=lambda item: item[0])

