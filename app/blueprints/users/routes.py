from app.blueprints.users import users_bp
from .schemas import user_schema, users_schema, login_schema
from flask import request, jsonify, render_template
from marshmallow import ValidationError
from app.models import Users, db
from app.extensions import limiter
from werkzeug.security import generate_password_hash, check_password_hash
from app.util.auth import encode_token, token_required



@users_bp.route('/login', methods=['POST'])
@limiter.limit("5 per 10 min")
def login():
    try:
        data = login_schema.load(request.json) # Send email and password
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    user = db.session.query(Users).where(Users.email==data['email']).first() #Search my db for a user with the passed in email

    if user and check_password_hash(user.password, data['password']): #Check the user stored password hash against the password that was sent
        token = encode_token(user.id, role=user.role)
        return jsonify({
            "message": f'Welcome {user.username}',
            "token": token
        }), 200
    
    return jsonify("Invalid email or password!"), 403


#CREATE USER ROUTE
@users_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
@limiter.limit("5 per day")
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    taken = db.session.query(Users).where(Users.email==data['email']).first()
    if taken: #Checks if I got a user from the query
        return jsonify({'message': 'email is taken'}), 400
    
    data['password'] = generate_password_hash(data['password']) #resetting the password key's value, to the hash of the current value

    new_user = Users(**data) #Creating User object
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

#Read Users
@users_bp.route('', methods=['GET']) #Endpoint to get user information
def read_users():
    users = db.session.query(Users).all()
    return users_schema.jsonify(users), 200


#Read Individual User - Using a Dynamic Endpoint
@users_bp.route('/profile', methods=['GET'])
@limiter.limit("15 per hour")
@token_required
def read_user():
    user_id = request.user_id
    user = db.session.get(Users, user_id)
    return user_schema.jsonify(user), 200


#Delete a User
@users_bp.route('', methods=['DELETE'])
@limiter.limit("5 per day")
@token_required
def delete_user():
    token_id = request.user_id #Grabbing token id from the request (We stored it there in the token_required wrapper)
    
    user = db.session.get(Users, token_id) #loook up whoever the token belongs to (aka whos logged in)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted user {token_id}"}), 200
   


#Update a User
@users_bp.route('', methods=['PUT'])
# @limiter.limit("1 per month")
@token_required
def update_user():
    user_id = request.user_id
    user = db.session.get(Users, user_id) #Query for our user to update

    if not user: #Checking if I got a user
        return jsonify({"message": "user not found"}), 404  #if not return error message
    
    try:
        user_data = user_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    user_data['password'] = generate_password_hash(user_data['password']) #resetting the password key's value, to the hash of the current value
    
    for key, value in user_data.items(): #Looping over attributes and values from user data dictionary
        setattr(user, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return user_schema.jsonify(user), 200
    
#Query the user by id
#Validate and Deserialze the updates that they are sending in the body of the request
#for each of the values that they are sending, we will change the value of the queried object
#commit the changes
#return a response

